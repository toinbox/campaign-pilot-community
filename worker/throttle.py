"""
Atomic Redis throttler using Lua scripts.

Lua script runs entirely inside Redis — atomically:
  1. INCR counter
  2. SET TTL only on first increment (avoids TTL race)
  3. Check limit — if exceeded, DECR and return 0
  4. All counters roll back if any limit is hit

This eliminates:
  - Pipeline non-atomicity
  - Budget leakage from partial rollbacks
  - Race conditions between parallel workers
  - TTL race (crash between INCR and EXPIRE)
"""

import os
import redis as redis_lib
from datetime import datetime, timezone

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

_redis = None


def get_redis():
    global _redis
    if _redis is None:
        _redis = redis_lib.from_url(REDIS_URL, decode_responses=True)
    return _redis


# ── Lua script ──────────────────────────────────────────────────────────────
# KEYS[1] = server hour key
# KEYS[2] = server day key
# KEYS[3] = domain hour key
# KEYS[4] = domain day key  (optional — pass empty string to skip)
# ARGV[1] = server hourly limit
# ARGV[2] = server daily limit
# ARGV[3] = domain hourly limit  (0 = no limit)
# ARGV[4] = domain daily limit   (0 = no limit)
# ARGV[5] = hour TTL in seconds  (3600)
# ARGV[6] = day TTL in seconds   (86400)
#
# Returns: 1 = slot acquired, 0 = limit hit

_LUA_ACQUIRE = """
local hour_ttl = tonumber(ARGV[5])
local day_ttl  = tonumber(ARGV[6])

-- Server hourly
local sh = redis.call("INCR", KEYS[1])
if sh == 1 then redis.call("EXPIRE", KEYS[1], hour_ttl) end
if sh > tonumber(ARGV[1]) then
    redis.call("DECR", KEYS[1])
    return 0
end

-- Server daily
local sd = redis.call("INCR", KEYS[2])
if sd == 1 then redis.call("EXPIRE", KEYS[2], day_ttl) end
if sd > tonumber(ARGV[2]) then
    redis.call("DECR", KEYS[1])
    redis.call("DECR", KEYS[2])
    return 0
end

-- Domain hourly (skip if limit == 0 or key empty)
if tonumber(ARGV[3]) > 0 and KEYS[3] ~= "" then
    local dh = redis.call("INCR", KEYS[3])
    if dh == 1 then redis.call("EXPIRE", KEYS[3], hour_ttl) end
    if dh > tonumber(ARGV[3]) then
        redis.call("DECR", KEYS[1])
        redis.call("DECR", KEYS[2])
        redis.call("DECR", KEYS[3])
        return 0
    end
end

-- Domain daily (skip if limit == 0 or key empty)
if tonumber(ARGV[4]) > 0 and KEYS[4] ~= "" then
    local dd = redis.call("INCR", KEYS[4])
    if dd == 1 then redis.call("EXPIRE", KEYS[4], day_ttl) end
    if dd > tonumber(ARGV[4]) then
        redis.call("DECR", KEYS[1])
        redis.call("DECR", KEYS[2])
        if tonumber(ARGV[3]) > 0 and KEYS[3] ~= "" then
            redis.call("DECR", KEYS[3])
        end
        redis.call("DECR", KEYS[4])
        return 0
    end
end

return 1
"""

_LUA_RELEASE = """
-- Release a previously acquired slot (call on send failure/retry)
-- KEYS[1..4] = same keys as acquire (with correct hour/day strings from acquire time)
-- ARGV[1..4] = limits (0 = skip)
local function safe_decr(key)
    if key ~= "" then
        local val = redis.call("GET", key)
        if val and tonumber(val) > 0 then
            redis.call("DECR", key)
        end
    end
end
safe_decr(KEYS[1])
safe_decr(KEYS[2])
if tonumber(ARGV[3]) > 0 then safe_decr(KEYS[3]) end
if tonumber(ARGV[4]) > 0 then safe_decr(KEYS[4]) end
return 1
"""

_acquire_script = None
_release_script = None


def _get_scripts():
    global _acquire_script, _release_script
    r = get_redis()
    if _acquire_script is None:
        _acquire_script = r.register_script(_LUA_ACQUIRE)
    if _release_script is None:
        _release_script = r.register_script(_LUA_RELEASE)
    return _acquire_script, _release_script


from zoneinfo import ZoneInfo

PRAGUE_TZ = ZoneInfo("Europe/Prague")


def _time_keys():
    """Return current Prague time hour and day strings for key namespacing."""
    now = datetime.now(PRAGUE_TZ)
    hour_str = now.strftime("%Y%m%d%H")
    day_str = now.strftime("%Y%m%d")
    return hour_str, day_str


def _day_ttl():
    """Return seconds until end of current Prague day (midnight Prague time)."""
    from datetime import datetime, timedelta
    now = datetime.now(PRAGUE_TZ)
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((midnight - now).total_seconds()))


def _hour_ttl():
    """Return seconds until end of current Prague hour."""
    from datetime import datetime, timedelta
    now = datetime.now(PRAGUE_TZ)
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return max(1, int((next_hour - now).total_seconds()))


def acquire_slot(server, domain, domain_limits=None):
    """
    Atomically reserve a send slot for server + domain.

    Args:
        server: dict with keys: id, hourly_limit, daily_limit, status, warmup_day
        domain: recipient domain string e.g. "gmail.com"
        domain_limits: dict with max_per_hour, max_per_day or None

    Returns:
        dict with 'keys' and 'args' — slot acquired, pass to release_slot on failure
        None — limit hit, do not send
    """
    hour_str, day_str = _time_keys()

    server_id = server["id"]
    hourly_limit = server["hourly_limit"]
    daily_limit = server["daily_limit"]

    # Warmup: override daily limit
    if server.get("status") == "warmup" and server.get("warmup_day", 0) > 0:
        warmup_limit = min(50 * (2 ** (server["warmup_day"] - 1)), daily_limit)
        daily_limit = warmup_limit

    # Domain limits
    dom_hour_limit = 0
    dom_day_limit = 0
    if domain_limits:
        dom_hour_limit = domain_limits.get("max_per_hour", 0)
        dom_day_limit = domain_limits.get("max_per_day", 0)

    keys = [
        f"throttle:server:{server_id}:hour:{hour_str}",
        f"throttle:server:{server_id}:day:{day_str}",
        f"throttle:domain:{domain}:hour:{hour_str}" if dom_hour_limit else "",
        f"throttle:domain:{domain}:day:{day_str}" if dom_day_limit else "",
    ]
    args = [
        hourly_limit,
        daily_limit,
        dom_hour_limit,
        dom_day_limit,
        _hour_ttl(),
        _day_ttl(),
    ]

    acquire, _ = _get_scripts()
    result = acquire(keys=keys, args=args)
    if result == 1:
        return {"keys": keys, "args": args}
    return None


def release_slot(slot):
    """
    Release a previously acquired slot using the exact keys from acquire time.
    Pass the dict returned by acquire_slot — ensures correct hour/day window even across hour boundary.
    """
    if not slot:
        return
    _, release = _get_scripts()
    release(keys=slot["keys"], args=slot["args"])


def get_server_counts(server_id):
    """Return current hour/day sent counts from Redis (for monitoring)."""
    hour_str, day_str = _time_keys()
    r = get_redis()
    hour_key = f"throttle:server:{server_id}:hour:{hour_str}"
    day_key = f"throttle:server:{server_id}:day:{day_str}"
    hour_val = r.get(hour_key)
    day_val = r.get(day_key)
    return {
        "sent_this_hour": int(hour_val) if hour_val else 0,
        "sent_today": int(day_val) if day_val else 0,
    }