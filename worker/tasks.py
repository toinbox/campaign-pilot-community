import time
import random
import smtplib
import sqlite3
import os
import logging
import socket
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate
from datetime import datetime, timedelta
from collections import deque, defaultdict
from jinja2 import Template

from worker.celery_app import celery_app
import hmac
import hashlib
from worker.throttle import acquire_slot, release_slot, get_server_counts, get_redis
import secrets
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/campaign_manager.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


# ══════════════════════════════════════════════════════════
# SERVER POOL MANAGER
# ══════════════════════════════════════════════════════════

class ServerPoolManager:
    """Manages server selection with rotation, health checks, and rate limiting."""

    def __init__(self, db, campaign_id):
        self.db = db
        self.campaign_id = campaign_id
        self._load_campaign()
        self._load_servers()
        self._batch_counter = 0
        self._current_server_idx = 0

    def _load_campaign(self):
        self.campaign = dict(self.db.execute(
            "SELECT * FROM campaigns WHERE id=?", (self.campaign_id,)
        ).fetchone())

    def _load_servers(self):
        self.servers =[dict(r) for r in self.db.execute("""
            SELECT s.* FROM servers s
            JOIN campaign_servers cs ON s.id = cs.server_id
            WHERE cs.campaign_id = ? AND s.status IN ('active', 'warmup')
                AND s.deleted_at IS NULL
            ORDER BY cs.priority
        """, (self.campaign_id,)).fetchall()]

    def _reset_counters_if_needed(self, server):
        """No-op: counters are managed by Redis TTL in throttle.py."""
        pass

    def _is_server_available(self, server):
        """Check server status only — rate limits are enforced atomically in acquire_slot."""
        if server["status"] not in ("active", "warmup"):
            return False
        # Quick Redis count check (non-atomic, just for pool filtering)
        counts = get_server_counts(server["id"])
        if counts["sent_this_hour"] >= server["hourly_limit"]:
            return False
        if counts["sent_today"] >= server["daily_limit"]:
            return False
        if server["status"] == "warmup" and server.get("warmup_day", 0) > 0:
            warmup_limit = min(50 * (2 ** (server["warmup_day"] - 1)), server["daily_limit"])
            if counts["sent_today"] >= warmup_limit:
                return False
        return True

    def get_next_server(self):
        """Select next server based on rotation mode."""
        mode = self.campaign["server_rotation_mode"]
        available = [s for s in self.servers if self._is_server_available(s)]

        if not available:
            return None

        if mode == "round_robin":
            # Indexujeme modulo počet dostupných serverů
            server = available[self._current_server_idx % len(available)]
            self._current_server_idx += 1
            return server

        elif mode == "batch":
            batch_size = self.campaign["server_batch_size"]

            # 1. Zjistíme, který server by měl být "na řadě" dle batche
            # Počet celých batches, které proběhly:
            total_batches_passed = self._current_server_idx 

            # 2. Vybereme server z dostupných (pokud index přeteče, začne od 0)
            server = available[total_batches_passed % len(available)]

            # 3. Inkrementujeme počítadlo v rámci aktuálního batche
            self._batch_counter += 1

            # 4. Pokud jsme vyčerpali batch, posuneme hlavní index serveru
            if self._batch_counter >= batch_size:
                self._batch_counter = 0
                self._current_server_idx += 1

            return server

        elif mode == "weighted":
            # ... logika zůstává ...
            total_weight = sum((s.get("weight") or 1) for s in available)
            pick = random.uniform(0, total_weight)
            current = 0
            for s in available:
                current += (s.get("weight") or 1)
                if pick <= current:
                    return s
            return available[-1]

        return available[0]

    def record_send(self, server_id):
        """No-op: slot was already counted atomically by acquire_slot in Redis."""
        pass

    def record_failure(self, server_id, error_type):
        """Log server failure and update health score (indicator only, never pauses)."""
        self.db.execute("""
            INSERT INTO server_health_log (server_id, event_type, detail)
            VALUES (?, ?, ?)
        """, (server_id, error_type, ""))
        self.db.commit()

        # Update health_score as indicator based on recent failures
        failures = self.db.execute("""
            SELECT COUNT(*) FROM server_health_log
            WHERE server_id = ? AND event_type IN ('bounce_spike', 'timeout', 'smtp_error')
                AND created_at > datetime('now', '-1 hour')
        """, (server_id,)).fetchone()[0]

        # Compute health: 100 = no failures, decreases by 10 per failure, floor at 0
        new_health = max(0, 100 - (failures * 10))
        self.db.execute(
            "UPDATE servers SET health_score = ? WHERE id = ?",
            (new_health, server_id)
        )
        self.db.commit()
        if failures >= 5:
            logger.warning(
                f"Server {server_id}: health_score={new_health} ({failures} failures in last hour)"
            )


# ══════════════════════════════════════════════════════════
# DESTINATION RATE LIMITER
# ══════════════════════════════════════════════════════════

def get_domain_limits(db, domain):
    """Fetch domain limits from DB (config only, counting is in Redis)."""
    row = db.execute(
        "SELECT max_per_hour, max_per_day FROM destination_limits WHERE domain = ?", (domain,)
    ).fetchone()
    if not row:
        return None
    return {"max_per_hour": row["max_per_hour"], "max_per_day": row["max_per_day"]}


def check_destination_limit(db, domain):
    """Kept for compatibility — actual enforcement is in acquire_slot."""
    return True  # enforce via acquire_slot


def record_destination_send(db, domain):
    """No-op — counting is handled atomically by acquire_slot in Redis."""
    pass


# ══════════════════════════════════════════════════════════
# EMAIL SENDER — fresh connection per email (Mailcow/Rspamd safe)
# ══════════════════════════════════════════════════════════

def send_email_smtp(server, to_email, subject, html_body, text_body="", unsubscribe_url=None, campaign_id=None):
    """Send a single email via SMTP. Returns (success, error_type_or_message_id).
    Fresh connection per email — no pooling. Mailcow + Rspamd requires full
    SMTP lifecycle per message (EHLO → AUTH → MAIL → DATA → QUIT).
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{server['from_name']} <{server['from_email']}>" if server["from_name"] else server["from_email"]
        msg["To"] = to_email
        msg["Subject"] = subject

        # Domain from sender email for Message-ID and List-Id
        domain = server["from_email"].split("@")[-1] if "@" in server["from_email"] else "localhost"

        # RFC-compliant headers for bulk mail
        msg["Message-ID"] = make_msgid(domain=domain)
        msg["Date"] = formatdate(localtime=True)
        msg["Precedence"] = "bulk"
        msg["Auto-Submitted"] = "auto-generated"
        msg["List-Id"] = f"<{domain}>"

        # Feedback-ID for Google Postmaster (campaign:server:domain)
        campaign_tag = str(campaign_id) if campaign_id else "0"
        msg["Feedback-ID"] = f"{campaign_tag}:{server['id']}:{domain}"

        # Abuse contact — transparency signal for Spamhaus and postmasters
        msg["X-Report-Abuse"] = f"Please report abuse to abuse@{domain}"
        msg["X-Complaints-To"] = f"abuse@{domain}"

        # List-Unsubscribe: HTTPS + mailto (RFC 8058 vyžaduje HTTPS pro One-Click)
        unsub_mailto = f"<mailto:{server['from_email']}?subject=Unsubscribe>"

        if unsubscribe_url:
            msg["List-Unsubscribe"] = f"<{unsubscribe_url}>, {unsub_mailto}"
        else:
            msg["List-Unsubscribe"] = unsub_mailto

        # Podpora pro moderní One-Click Unsubscribe (RFC 8058)
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        if not text_body:
            import re as _re
            _t = _re.sub(r"<style[^>]*>.*?</style>", "", html_body, flags=_re.DOTALL)
            _t = _re.sub(r"<[^>]+>", " ", _t)
            _t = " ".join(_t.split())
            text_body = _t.strip()

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Fresh connection per email — proper EHLO, TLS, AUTH, send, QUIT
        envelope_from = server["from_email"]
        with smtplib.SMTP(server["smtp_host"], server["smtp_port"], timeout=120, local_hostname=domain) as smtp:
            smtp.ehlo(domain)
            if server["use_tls"]:
                smtp.starttls()
                smtp.ehlo(domain)
            smtp.login(server["smtp_user"], server["smtp_password"])
            smtp.sendmail(envelope_from, [to_email], msg.as_string())

        return True, msg["Message-ID"] or ""

    except smtplib.SMTPRecipientsRefused as e:
        error_str = str(e)
        for addr, (code, msg_text) in e.recipients.items():
            decoded = msg_text.decode('utf-8', errors='ignore')
            if any(kw in decoded.lower() for kw in [
                'poor reputation', 'blacklisted', 'access to this mail',
                'rejected due to', 'spam policy', 'spamhaus'
            ]):
                return False, f"reputation_block: {code} {decoded}"
            if code >= 550:
                return False, f"hard_bounce: {code} {decoded}"
            elif code >= 400:
                return False, f"soft_bounce: {code} {decoded}"
        return False, f"hard_bounce: {error_str}"
    except smtplib.SMTPSenderRefused as e:
        return False, f"smtp_error: Sender refused: {str(e)}"
    except smtplib.SMTPDataError as e:
        code = e.smtp_code if hasattr(e, 'smtp_code') else 0
        if code >= 550:
            return False, f"hard_bounce: {str(e)}"
        return False, f"soft_bounce: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"smtp_error: {str(e)}"
    except Exception as e:
        return False, f"error: {str(e)}"

# ══════════════════════════════════════════════════════════
# MAIN CAMPAIGN TASK
# ══════════════════════════════════════════════════════════

@celery_app.task(bind=True, max_retries=0)
def run_campaign(self, campaign_id):
    """Execute a campaign with throttled sending and server rotation."""
    # ── Redis distributed lock ──
    # Philosophy: when in doubt, do NOT touch the lock and bail out.
    # Previous logic deleted the lock on any inspect() failure, which caused
    # two workers to run the same campaign when the broker was slow.
    lock_key = f"lock:campaign:{campaign_id}"
    lock_value = self.request.id  # unique per task invocation
    LOCK_TTL = 7200  # 2h — refreshed every minute by heartbeat below

    try:
        r_lock = get_redis()
    except Exception as e:
        logger.error(f"Campaign {campaign_id}: Redis unavailable, aborting: {e}")
        return

    try:
        # Fast path: try to acquire atomically. No pre-check → no TOCTOU.
        acquired = r_lock.set(lock_key, lock_value, nx=True, ex=LOCK_TTL)

        if not acquired:
            # Someone else holds the lock. Verify if they're still alive.
            existing = r_lock.get(lock_key)
            if existing is None:
                # Race: holder released between set() and get(). Retry once.
                acquired = r_lock.set(lock_key, lock_value, nx=True, ex=LOCK_TTL)
                if not acquired:
                    logger.info(f"Campaign {campaign_id}: lock race lost, skipping")
                    return
            else:
                existing_task_id = existing.decode() if isinstance(existing, bytes) else existing
                if existing_task_id == lock_value:
                    # Same task_id — either (a) crash-recovery redelivery (previous
                    # attempt on a dead worker/slot) or (b) visibility_timeout redelivery
                    # while the previous attempt is STILL RUNNING somewhere.
                    # Case (b) is the "campaign taken by extra workers" bug.
                    try:
                        i = celery_app.control.inspect(timeout=5)
                        active = i.active()
                    except Exception as e:
                        logger.warning(
                            f"Campaign {campaign_id}: redelivery check failed ({e}), bailing"
                        )
                        return
                    if active is None:
                        logger.warning(
                            f"Campaign {campaign_id}: redelivery but inspect inconclusive, bailing"
                        )
                        return
                    # Count ALL instances of our task_id in active() — do NOT filter by
                    # hostname: with --concurrency=N all slots share the same hostname,
                    # so a same-hostname redelivery to a different slot is a real duplicate.
                    # We expect to see ourselves exactly once in active(); >1 means a twin.
                    total_instances = sum(
                        1
                        for worker_tasks in active.values()
                        for t in worker_tasks
                        if t.get("id") == lock_value
                    )
                    if total_instances > 1:
                        logger.warning(
                            f"Campaign {campaign_id}: redelivered while {total_instances - 1} "
                            f"other instance(s) of task {lock_value} still running — broker "
                            f"visibility_timeout likely too short. Bailing to prevent duplicate run."
                        )
                        return
                    # Previous attempt is truly gone — take over in place.
                else:
                    # Is the holder actually running? Use inspect — but on ANY
                    # ambiguity, bail out instead of stealing the lock.
                    try:
                        i = celery_app.control.inspect(timeout=5)
                        active = i.active()
                    except Exception as e:
                        logger.warning(
                            f"Campaign {campaign_id}: inspect() failed ({e}), "
                            f"assuming lock holder {existing_task_id} is alive, skipping"
                        )
                        return

                    if active is None:
                        logger.warning(
                            f"Campaign {campaign_id}: no worker responded to inspect, "
                            f"assuming lock holder is alive, skipping"
                        )
                        return

                    active_ids = {t["id"] for tasks in active.values() for t in tasks}
                    if existing_task_id in active_ids:
                        logger.info(
                            f"Campaign {campaign_id}: already running as {existing_task_id}, skipping"
                        )
                        return

                    # Holder confirmed dead — atomic compare-and-swap steal.
                    # (If the lock has changed hands since we read it, bail.)
                    steal_script = """
                        if redis.call('GET', KEYS[1]) == ARGV[1] then
                            redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])
                            return 1
                        end
                        return 0
                    """
                    try:
                        stolen = r_lock.eval(
                            steal_script, 1, lock_key,
                            existing_task_id, lock_value, LOCK_TTL
                        )
                    except Exception as e:
                        logger.warning(f"Campaign {campaign_id}: lock steal failed ({e}), skipping")
                        return
                    if not stolen:
                        logger.info(f"Campaign {campaign_id}: lock changed during takeover, skipping")
                        return
                    logger.warning(
                        f"Campaign {campaign_id}: took over lock from dead task {existing_task_id}"
                    )
    except Exception as e:
        logger.error(f"Campaign {campaign_id}: lock acquisition error: {e}")
        return

    # Track the last heartbeat so we can refresh the lock TTL periodically.
    # Needed because campaigns with long batch pauses can exceed LOCK_TTL.
    last_heartbeat = time.time()

    def heartbeat():
        """Refresh lock TTL if we still own it. Call periodically from the main loop."""
        nonlocal last_heartbeat
        if time.time() - last_heartbeat < 60:
            return
        try:
            refresh_script = """
                if redis.call('GET', KEYS[1]) == ARGV[1] then
                    return redis.call('EXPIRE', KEYS[1], ARGV[2])
                end
                return 0
            """
            r_lock.eval(refresh_script, 1, lock_key, lock_value, LOCK_TTL)
            last_heartbeat = time.time()
        except Exception as e:
            logger.warning(f"Campaign {campaign_id}: lock heartbeat failed: {e}")

    db = get_db()

    try:
        # Load campaign
        _camp_row = db.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        if not _camp_row:
            logger.error(f"Campaign {campaign_id}: not found in DB")
            return
        campaign = dict(_camp_row)

        if campaign["status"] != "running":
            logger.info(f"Campaign {campaign_id} is not running (status: {campaign['status']}), skipping")
            return

        # Load template
        _tpl_row = db.execute(
            "SELECT * FROM email_templates WHERE id=?", (campaign["template_id"],)
        ).fetchone()
        template = dict(_tpl_row)

        # Load recipients (active contacts in list, not yet sent, optional country filter)
        target_country = campaign.get("target_country", "") or ""
        if target_country and target_country != "OTHER":
            recipients = db.execute("""
                SELECT c.* FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                    AND c.geo_country_code = ?
                    AND c.id NOT IN (
                        SELECT contact_id FROM send_log WHERE campaign_id = ?
                    )
                ORDER BY c.id
            """, (campaign["list_id"], target_country, campaign_id)).fetchall()
        elif target_country == "OTHER":
            recipients = db.execute("""
                SELECT c.* FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                    AND c.geo_country_code NOT IN ('CZ','SK','DE','AT','PL','HU')
                    AND c.geo_country_code != ''
                    AND c.id NOT IN (
                        SELECT contact_id FROM send_log WHERE campaign_id = ?
                    )
                ORDER BY c.id
            """, (campaign["list_id"], campaign_id)).fetchall()
        else:
            recipients = db.execute("""
                SELECT c.* FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                    AND c.id NOT IN (
                        SELECT contact_id FROM send_log WHERE campaign_id = ?
                    )
                ORDER BY c.id
            """, (campaign["list_id"], campaign_id)).fetchall()

        if not recipients:
            db.execute(
                "UPDATE campaigns SET status='completed', completed_at=datetime('now') WHERE id=?",
                (campaign_id,)
            )
            db.commit()
            logger.info(f"Campaign {campaign_id} completed - no more recipients")
            return

        # Check how many recipients are on blocked domains
        available = [r for r in recipients if not db.execute(
            "SELECT 1 FROM destination_limits WHERE domain=? AND blocked=1",
            (dict(r)["email"].split("@")[-1].lower(),)
        ).fetchone()]

        if not available:
            logger.info(f"Campaign {campaign_id}: all remaining recipients on blocked domains — completing")
            db.execute("UPDATE campaigns SET status='completed', completed_at=datetime('now') WHERE id=?", (campaign_id,))
            db.commit()
            return

        # Initialize server pool
        pool = ServerPoolManager(db, campaign_id)

        if not pool.servers:
            logger.error(f"Campaign {campaign_id}: No servers available")
            db.execute("UPDATE campaigns SET status='paused', pause_reason='system' WHERE id=?", (campaign_id,))
            db.commit()
            return

        # Throttle settings - manual intervals + batch pause
        batch_size = campaign["throttle_total"]
        interval_min = campaign["throttle_interval_min"]
        interval_max = campaign["throttle_interval_max"]
        batch_pause_seconds = campaign["throttle_window_minutes"] * 60  # pause between batches
        sent_in_batch = 0

        avg_interval = (interval_min + interval_max) / 2
        est_batch_time = batch_size * avg_interval / 60

        logger.info(
            f"Campaign {campaign_id}: Starting send to {len(recipients)} recipients, "
            f"batch={batch_size}, interval={interval_min}-{interval_max}s, "
            f"batch_pause={campaign['throttle_window_minutes']}min, "
            f"est_batch_time={est_batch_time:.1f}min"
        )

        # base_url: per-server tracking_domain if set, otherwise APP_BASE_URL
        default_base_url = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")
        secret_key = os.getenv("SECRET_KEY", "change-me").encode()

        # Single unified work queue — retry is just re-queuing, not a second pass
        work_queue = deque(recipients)
        retry_attempts = defaultdict(int)
        MAX_RETRY = 3

        while work_queue:
            contact_row = work_queue.popleft()
            contact = dict(contact_row)

            # Keep the Redis lock alive during long campaigns
            heartbeat()

            # Check if campaign was paused/cancelled
            current_status = db.execute(
                "SELECT status FROM campaigns WHERE id=?", (campaign_id,)
            ).fetchone()[0]
            if current_status != "running":
                logger.info(f"Campaign {campaign_id} status changed to {current_status}, stopping")
                break

            # Check batch limit - pause between batches
            if sent_in_batch >= batch_size:
                if batch_pause_seconds > 0:
                    logger.info(
                        f"Campaign {campaign_id}: Batch of {batch_size} done, "
                        f"pausing {campaign['throttle_window_minutes']} min before next batch"
                    )
                    # Sleep in chunks so lock heartbeat can refresh during long pauses
                    end_at = time.time() + batch_pause_seconds
                    while time.time() < end_at:
                        time.sleep(min(30, end_at - time.time()))
                        heartbeat()
                sent_in_batch = 0

            # Get domain and its limits (config from DB, enforcement in Redis)
            domain = contact["email"].split("@")[-1].lower()
            domain_limits = get_domain_limits(db, domain)

            # Get server — if none available due to rate limits, WAIT in running state.
            # Per user requirement: campaign must stay 'running' and auto-resume when
            # limits reset. It should only pause if a real server-config problem
            # exists (e.g. all assigned servers deleted/paused/blacklisted).
            server = pool.get_next_server()
            while not server:
                # Is there any assigned server still usable (active/warmup)?
                # If not, this is a real config problem — pause and bail.
                usable = [s for s in pool.servers if s["status"] in ("active", "warmup")]
                if not usable:
                    logger.error(
                        f"Campaign {campaign_id}: no active/warmup servers assigned — pausing"
                    )
                    db.execute(
                        "UPDATE campaigns SET status='paused', pause_reason='no_active_servers' WHERE id=?",
                        (campaign_id,)
                    )
                    db.commit()
                    server = None
                    break

                # Rate-limit case: compute wait time until the next HOURLY reset.
                # Hourly counters reset at the top of each Prague hour — never more
                # than 60 minutes away. If every server is also over its daily cap,
                # the next hour won't help, so wait until midnight Prague instead.
                from datetime import datetime as _dt, timedelta as _td
                from zoneinfo import ZoneInfo as _ZI
                _prague = _ZI("Europe/Prague")
                _now = _dt.now(_prague)

                _all_daily_capped = all(
                    get_server_counts(s["id"])["sent_today"] >= s["daily_limit"]
                    for s in usable
                )
                if _all_daily_capped:
                    _target = (_now + _td(days=1)).replace(
                        hour=0, minute=0, second=5, microsecond=0
                    )
                    _reason = "daily"
                else:
                    _target = (_now + _td(hours=1)).replace(
                        minute=0, second=5, microsecond=0
                    )
                    _reason = "hourly"
                _wait_s = max(30, int((_target - _now).total_seconds()))
                logger.info(
                    f"Campaign {campaign_id}: all servers at {_reason} limit, "
                    f"waiting {_wait_s}s until {_target.strftime('%Y-%m-%d %H:%M:%S')} Prague"
                )

                # Sleep in small chunks — heartbeat lock, honor user pause/cancel.
                _end = time.time() + _wait_s
                while time.time() < _end:
                    time.sleep(min(30, _end - time.time()))
                    heartbeat()
                    _cs = db.execute(
                        "SELECT status FROM campaigns WHERE id=?", (campaign_id,)
                    ).fetchone()[0]
                    if _cs != "running":
                        logger.info(
                            f"Campaign {campaign_id}: status changed to {_cs} during wait"
                        )
                        break

                # Bail entire main loop if user paused/cancelled during the wait.
                _cs = db.execute(
                    "SELECT status FROM campaigns WHERE id=?", (campaign_id,)
                ).fetchone()[0]
                if _cs != "running":
                    server = None
                    break

                # Reload server list (status may have changed in DB) and retry.
                pool._load_servers()
                server = pool.get_next_server()
                # If still none and we waited for an hourly reset, loop will
                # re-evaluate — typically the next pass finds a server, but if
                # somebody paused all servers from the UI mid-wait, next loop
                # iteration will see 'usable == []' and pause cleanly.

            if server is None:
                # Either status changed (pause/cancel) or no active servers.
                # Both cases already logged/handled above — just exit main loop.
                break

            # Skip domain if reputation block is active (manual block in DB)
            blocked = db.execute(
                "SELECT block_reason FROM destination_limits WHERE domain=? AND blocked=1",
                (domain,)
            ).fetchone()
            if blocked:
                logger.info(f"Campaign {campaign_id}: skipping {contact['email']} — domain {domain} blocked")
                # Insert blocked record — server_id MUST be NULL (not 0):
                # send_log.server_id has FK → servers(id) with foreign_keys=ON,
                # and no server has id=0, so passing 0 raises IntegrityError,
                # which previously propagated out of the loop and paused the whole campaign.
                # INSERT OR IGNORE prevents duplicates (UNIQUE campaign_id, contact_id).
                try:
                    result = db.execute(
                        "INSERT OR IGNORE INTO send_log (campaign_id, contact_id, server_id, status) VALUES (?, ?, NULL, 'blocked')",
                        (campaign_id, contact["id"])
                    )
                    if result.rowcount > 0:
                        db.execute("UPDATE campaigns SET blocked_count = blocked_count + 1 WHERE id=?", (campaign_id,))
                    db.commit()
                except Exception as e:
                    # Never let logging a blocked record crash the campaign — just skip this contact
                    logger.error(f"Campaign {campaign_id}: failed to log blocked record for {contact['email']}: {e}")
                    try:
                        db.rollback()
                    except Exception:
                        pass
                continue

            # Atomically acquire send slot (server + domain limits via Lua/Redis)
            try:
                slot = acquire_slot(server, domain, domain_limits)
            except Exception as e:
                logger.error(f"Campaign {campaign_id}: Redis throttle error: {e} — pausing campaign")
                db.execute("UPDATE campaigns SET status='paused', pause_reason='system' WHERE id=?", (campaign_id,))
                db.commit()
                break

            if not slot:
                if retry_attempts[contact["id"]] < MAX_RETRY:
                    retry_attempts[contact["id"]] += 1
                    work_queue.append(contact_row)  # back to end of same queue
                    logger.info(
                        f"Campaign {campaign_id}: Rate limit, requeued "
                        f"{retry_attempts[contact['id']]}/{MAX_RETRY} {contact['email']}"
                    )
                else:
                    logger.warning(f"Campaign {campaign_id}: Max retries for {contact['email']}, skipping")
                time.sleep(0.5)
                continue

            # Render template with contact data
            # Per-server base URL — tracking_domain if set, otherwise APP_BASE_URL
            base_url = (server.get("tracking_domain") or "").rstrip("/") or default_base_url
            # Compute unsubscribe token once per contact (not 3x)
            unsub_token = hmac.new(
                secret_key,
                f"{contact['id']}:{campaign_id}".encode(),
                hashlib.sha256
            ).hexdigest()
            unsubscribe_url = f"{base_url}/unsubscribe/{unsub_token}/{contact['id']}/{campaign_id}"

            try:
                render_ctx = dict(
                    first_name=contact["first_name"],
                    last_name=contact["last_name"],
                    company=contact["company"],
                    email=contact["email"],
                    unsubscribe_url=unsubscribe_url,
                )
                subject = Template(template["subject"]).render(**render_ctx)
                html_body = Template(template["html_body"]).render(**render_ctx)
                text_body = Template(template["text_body"] or "").render(**render_ctx)

                # Inject preheader using standard technique
                preheader = template.get("preheader", "") or ""
                if preheader:
                    preheader_html = (
                        '<span style="display:none;font-size:0;line-height:0;">'
                        f'{preheader}'
                        '</span>'
                    )
                    if "<body>" in html_body:
                        html_body = html_body.replace("<body>", "<body>" + preheader_html, 1)
                    elif "<body " in html_body:
                        import re as _re2
                        html_body = _re2.sub(r'(<body[^>]*>)', r'' + preheader_html, html_body, count=1)
                    else:
                        html_body = preheader_html + html_body
            except Exception as e:
                logger.error(f"Template render error for {contact['email']}: {e}")
                continue

            # Atomic dedup claim via DB — INSERT OR IGNORE + check rowcount
            # If another worker already started this contact, rowcount=0 → skip
            claim = db.execute("""
                INSERT OR IGNORE INTO send_log (campaign_id, contact_id, server_id, status)
                VALUES (?, ?, ?, 'sending')
            """, (campaign_id, contact["id"], server["id"]))
            if claim.rowcount == 0:
                logger.info(f"Campaign {campaign_id}: contact {contact['email']} already claimed, skipping")
                continue
            log_id = claim.lastrowid

            # ── Open & Click Tracking ──
            tracking_token = secrets.token_urlsafe(32)
            db.execute(
                "INSERT INTO email_tracking_tokens (token, send_log_id, campaign_id, contact_id) VALUES (?,?,?,?)",
                (tracking_token, log_id, campaign_id, contact["id"])
            )

            # ── Unsubscribe footer pojistka ──
            # Pokud šablona neobsahuje {{unsubscribe_url}}, přidáme patičku automaticky
            if "{{unsubscribe_url}}" not in template["html_body"] and unsubscribe_url not in html_body:
                unsub_footer = (
                    '<div style="text-align:center;font-size:12px;color:#999;'
                    'margin-top:30px;padding-top:20px;border-top:1px solid #eee;">'
                    f'Nechcete dostávat tyto emaily? '
                    f'<a href="{unsubscribe_url}" style="color:#999;">Odhlásit se z odběru</a>'
                    '</div>'
                )
                if "</body>" in html_body:
                    html_body = html_body.replace("</body>", unsub_footer + "</body>")
                elif "</BODY>" in html_body:
                    html_body = html_body.replace("</BODY>", unsub_footer + "</BODY>")
                else:
                    html_body = html_body + unsub_footer

            # Replace href links with click-tracking redirects (skip mailto/# links)
            def wrap_link(m):
                url = m.group(1)
                if url.startswith(("mailto:", "#")):
                    return m.group(0)
                click_url = base_url + "/track/click/" + tracking_token + "?url=" + quote(url, safe="")
                return 'href="' + click_url + '"'
            tracked_html = re.sub(r'href="([^"]*)"', wrap_link, html_body)

            # Inject 1x1 open-tracking pixel before </body>
            pixel = '<img src="' + base_url + '/track/open/' + tracking_token + '" width="1" height="1" style="display:none" alt="">'
            if "</body>" in tracked_html:
                tracked_html = tracked_html.replace("</body>", pixel + "</body>")
            elif "</BODY>" in tracked_html:
                tracked_html = tracked_html.replace("</BODY>", pixel + "</BODY>")
            else:
                tracked_html = tracked_html + pixel

            # Send
            success, result = send_email_smtp(server, contact["email"], subject, tracked_html, text_body, unsubscribe_url, campaign_id)

            if success:
                db.execute("""
                    UPDATE send_log SET status='delivered', message_id=?, sent_at=datetime('now')
                    WHERE id=?
                """, (result, log_id))
                db.execute("""
                    UPDATE campaigns SET sent_count = sent_count + 1, delivered = delivered + 1
                    WHERE id=?
                """, (campaign_id,))
                pool.record_send(server["id"])
            else:
                # Determine bounce type from error
                is_hard_bounce = result.startswith("hard_bounce:")
                is_soft_bounce = result.startswith("soft_bounce:")
                is_reputation_block = result.startswith("reputation_block:")
                is_bounce = is_hard_bounce or is_soft_bounce

                log_status = "bounced" if is_bounce else "failed"
                db.execute("""
                    UPDATE send_log SET status=?, error_message=?, sent_at=datetime('now')
                    WHERE id=?
                """, (log_status, result, log_id))

                if is_hard_bounce:
                    # Hard bounce - mark contact as bounced immediately
                    db.execute("""
                        UPDATE contacts SET status='bounced', bounce_count=bounce_count+1,
                            last_bounce_at=datetime('now'), bounce_type='hard'
                        WHERE id=?
                    """, (contact["id"],))
                    db.execute("UPDATE campaigns SET bounced = bounced + 1, sent_count = sent_count + 1 WHERE id=?", (campaign_id,))
                    pool.record_send(server["id"])  # Still counts as sent
                    logger.warning(f"Hard bounce: {contact['email']} - {result}")
                elif is_soft_bounce:
                    # Soft bounce - increment counter, mark bounced after 3
                    db.execute("""
                        UPDATE contacts SET bounce_count=bounce_count+1,
                            last_bounce_at=datetime('now'), bounce_type='soft'
                        WHERE id=?
                    """, (contact["id"],))
                    # Check if 3+ soft bounces
                    bc = db.execute("SELECT bounce_count FROM contacts WHERE id=?", (contact["id"],)).fetchone()[0]
                    if bc >= 3:
                        db.execute("UPDATE contacts SET status='bounced' WHERE id=?", (contact["id"],))
                    db.execute("UPDATE campaigns SET bounced = bounced + 1, sent_count = sent_count + 1 WHERE id=?", (campaign_id,))
                    pool.record_send(server["id"])
                    logger.warning(f"Soft bounce ({bc}x): {contact['email']} - {result}")
                elif is_reputation_block:
                    # Reputační blokace — chyba odesílatele, ne příjemce
                    # Kontakt zůstane active, doména se automaticky zablokuje v DB
                    release_slot(slot)
                    db.execute("UPDATE campaigns SET failed = failed + 1 WHERE id=?", (campaign_id,))
                    try:
                        block_domain = contact["email"].split("@")[-1].lower()
                        # Automatická blokace domény v DB
                        db.execute("""
                            UPDATE destination_limits SET blocked=1, block_reason=?
                            WHERE domain=? AND blocked=0
                        """, (result[:200], block_domain))
                        if db.execute("SELECT changes()").fetchone()[0] > 0:
                            logger.warning(f"Domain {block_domain} automatically blocked: {result[:100]}")
                        db.commit()
                        # Také uložit do Redis pro rychlou kontrolu
                        r.set(f"block:domain:{block_domain}", result[:200], ex=86400)
                    except Exception as ex:
                        logger.error(f"Failed to block domain: {ex}")
                else:
                    # Server/connection error - don't mark contact, it's not their fault
                    # Release slot back since email was never sent
                    release_slot(slot)
                    db.execute("UPDATE campaigns SET failed = failed + 1 WHERE id=?", (campaign_id,))
                    pool.record_failure(server["id"], "smtp_error")

            db.commit()
            sent_in_batch += 1  # count every SMTP attempt regardless of result

            # Throttle: random sleep between configured min and max interval
            sleep_time = random.uniform(interval_min, interval_max)
            time.sleep(sleep_time)


        # Check if campaign is done
        remaining = db.execute("""
            SELECT COUNT(*) FROM contacts c
            JOIN contact_list_members clm ON c.id = clm.contact_id
            WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                AND c.id NOT IN (SELECT contact_id FROM send_log WHERE campaign_id = ?)
        """, (campaign["list_id"], campaign_id)).fetchone()[0]

        if remaining == 0:
            db.execute(
                "UPDATE campaigns SET status='completed', completed_at=datetime('now') WHERE id=?",
                (campaign_id,)
            )
            db.commit()
            logger.info(f"Campaign {campaign_id} completed successfully")

    except Exception as e:
        logger.exception(f"Campaign {campaign_id} error: {e}")
        db.execute("UPDATE campaigns SET status='paused', pause_reason='system' WHERE id=?", (campaign_id,))
        db.commit()
    finally:
        db.close()
        # Atomic release: only delete if we still own the lock.
        # Prevents a race where our lock expired and someone else acquired it.
        try:
            release_script = """
                if redis.call('GET', KEYS[1]) == ARGV[1] then
                    return redis.call('DEL', KEYS[1])
                end
                return 0
            """
            r_lock.eval(release_script, 1, lock_key, lock_value)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
# PERIODIC TASKS
# ══════════════════════════════════════════════════════════

@celery_app.task
def reset_server_counters():
    """No-op: Redis keys expire automatically via TTL. Kept for beat schedule compatibility."""
    pass


@celery_app.task
def reset_daily_counters():
    """Advance warmup day for warmup servers. Reset pool account daily counters."""
    db = get_db()
    try:
        db.execute("""
            UPDATE servers SET warmup_day = warmup_day + 1
            WHERE status = 'warmup' AND deleted_at IS NULL
        """)
        # Reset pool account daily send counters
        db.execute("""
            UPDATE pool_accounts SET sent_today = 0, last_day_reset = date('now')
            WHERE deleted_at IS NULL AND (last_day_reset IS NULL OR last_day_reset < date('now'))
        """)
        db.commit()
    finally:
        db.close()


@celery_app.task
def check_scheduled_campaigns():
    """Start campaigns that are scheduled for now."""
    db = get_db()
    try:
        campaigns = db.execute("""
            SELECT id FROM campaigns
            WHERE status = 'scheduled' AND scheduled_at <= datetime('now') AND deleted_at IS NULL
        """).fetchall()

        for c in campaigns:
            db.execute("UPDATE campaigns SET status='running', started_at=datetime('now') WHERE id=?", (c["id"],))
            db.commit()
            run_campaign.delay(c["id"])
            logger.info(f"Started scheduled campaign {c['id']}")

        # ── Zombie detection ─────────────────────────────────────────
        # Find campaigns marked 'running' in DB whose Celery task isn't alive
        # and restart them. Principle: when inspect is inconclusive, do NOTHING
        # — it is safer to leave a real zombie alone for one cycle than to
        # mass-restart legitimate campaigns on a flaky broker.
        try:
            inspect = celery_app.control.inspect(timeout=5)
            active = inspect.active()
        except Exception as e:
            logger.warning(f"Watchdog: inspect() raised {e}, skipping zombie check this cycle")
            active = None

        if active is None:
            # No workers responded (broker slow, workers busy, etc.) — skip.
            logger.info("Watchdog: inspect inconclusive, skipping zombie check this cycle")
        else:
            active_campaign_ids = set()
            for worker_tasks in active.values():
                for t in worker_tasks:
                    if t.get("name") == "worker.tasks.run_campaign":
                        args = t.get("args", [])
                        if args:
                            active_campaign_ids.add(args[0])

            # Only consider campaigns that have been running for at least 2 minutes —
            # prevents a race where we just dispatched the task above and Celery
            # hasn't registered it in active() yet.
            running = db.execute("""
                SELECT id, name FROM campaigns
                WHERE status = 'running' AND deleted_at IS NULL
                  AND (started_at IS NULL OR datetime(started_at) < datetime('now', '-2 minutes'))
            """).fetchall()

            r_check = get_redis()
            for c in running:
                if c["id"] in active_campaign_ids:
                    continue
                # Extra safety: if a lock still exists and its owner is in the
                # active set (under a different campaign-id attribution), skip.
                lock_key = f"lock:campaign:{c['id']}"
                try:
                    lock_val = r_check.get(lock_key)
                    if lock_val:
                        lock_task_id = lock_val.decode() if isinstance(lock_val, bytes) else lock_val
                        all_active_task_ids = {
                            t["id"]
                            for worker_tasks in active.values()
                            for t in worker_tasks
                        }
                        if lock_task_id in all_active_task_ids:
                            # Lock is held by a live task — somehow args didn't match,
                            # but the holder is definitely alive. Don't touch.
                            continue
                    r_check.delete(lock_key)
                except Exception as e:
                    logger.warning(f"Watchdog: lock check for campaign {c['id']} failed: {e}")
                    continue
                logger.warning(f"Campaign {c['id']} ({c['name']}): zombie detected — restarting")
                run_campaign.delay(c["id"])
        # ── Clean up old Redis throttle keys ─────────────────────────
        # Runs every minute but only deletes stale keys — safe and fast
        try:
            from datetime import datetime
            from zoneinfo import ZoneInfo
            r_clean = get_redis()
            today = datetime.now(ZoneInfo("Europe/Prague")).strftime("%Y%m%d")
            deleted = 0
            for key in r_clean.scan_iter("throttle:*"):
                key_str = key.decode() if isinstance(key, bytes) else str(key)
                if today not in key_str:
                    r_clean.delete(key)
                    deleted += 1
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} stale Redis throttle keys")
        except Exception as e:
            logger.warning(f"Redis throttle cleanup error: {e}")

    finally:
        db.close()


@celery_app.task
def check_bounces():
    """Check IMAP mailboxes for bounce messages and mark contacts as bounced."""
    import imaplib
    import email
    from email import policy
    import re

    db = get_db()
    try:
        servers = db.execute("""
            SELECT * FROM servers
            WHERE bounce_check_enabled = 1 AND bounce_imap_host != ''
                AND deleted_at IS NULL
        """).fetchall()

        for server in servers:
            server = dict(server)
            total_bounces = 0
            try:
                # Connect to IMAP
                if server["bounce_imap_ssl"]:
                    imap = imaplib.IMAP4_SSL(server["bounce_imap_host"], server["bounce_imap_port"])
                else:
                    imap = imaplib.IMAP4(server["bounce_imap_host"], server["bounce_imap_port"])

                imap.login(server["bounce_imap_user"], server["bounce_imap_password"])
                imap.select("INBOX")

                # Search for bounce messages (DSN / delivery status notifications)
                # Common patterns: mailer-daemon, postmaster, delivery failure
                status, messages = imap.search(None, '(OR FROM "mailer-daemon" FROM "postmaster")')

                if status != "OK" or not messages[0]:
                    imap.close()
                    imap.logout()
                    db.execute(
                        "UPDATE servers SET bounce_last_check = datetime('now') WHERE id = ?",
                        (server["id"],)
                    )
                    db.commit()
                    continue

                msg_ids = messages[0].split()
                # Process last 100 bounce messages max
                for msg_id in msg_ids[-100:]:
                    try:
                        status, msg_data = imap.fetch(msg_id, "(RFC822)")
                        if status != "OK":
                            continue

                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email, policy=policy.default)

                        # Extract bounced email address from message body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() in ("text/plain", "message/delivery-status"):
                                    try:
                                        body += part.get_content()
                                    except Exception:
                                        try:
                                            body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                        except Exception:
                                            pass
                        else:
                            try:
                                body = msg.get_content()
                            except Exception:
                                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                        # Find email addresses in bounce message
                        bounced_emails = re.findall(
                            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                            body
                        )

                        # Determine bounce type from keywords
                        body_lower = body.lower()

                        # Reputační blokace — není chyba příjemce, zablokovat doménu
                        is_reputation = any(kw in body_lower for kw in [
                            "poor reputation", "blacklisted", "access to this mail",
                            "rejected due to", "spam policy", "spamhaus",
                        ])
                        if is_reputation:
                            # Automaticky zablokovat doménu příjemce
                            for rep_email in bounced_emails:
                                rep_email = rep_email.lower()
                                if rep_email in (server["from_email"], server["smtp_user"], server["bounce_imap_user"]):
                                    continue
                                if rep_email.startswith(("mailer-daemon@", "postmaster@")):
                                    continue
                                if "@" not in rep_email:
                                    continue
                                rep_domain = rep_email.split("@")[-1]
                                result = db.execute(
                                    "UPDATE destination_limits SET blocked=1, block_reason='Reputační blokace (automaticky)' WHERE domain=? AND blocked=0",
                                    (rep_domain,)
                                )
                                if result.rowcount > 0:
                                    logger.warning(f"Domain {rep_domain} auto-blocked due to reputation DSN")
                                    db.commit()
                            imap.store(msg_id, '+FLAGS', '(\\Seen \\Deleted)')
                            continue

                        is_hard = any(kw in body_lower for kw in[
                            "user unknown", "no such user", "mailbox not found",
                            "address rejected", "does not exist", "invalid address",
                            "recipient rejected", "550", "551", "552", "553", "554",
                            "permanent", "failed permanently",
                        ])
                        bounce_type = "hard" if is_hard else "soft"

                        # Mark contacts as bounced
                        for bounced_email in bounced_emails:
                            bounced_email = bounced_email.lower()
                            # Skip our own addresses and common system addresses
                            if bounced_email in (server["from_email"], server["smtp_user"],
                                                 server["bounce_imap_user"]):
                                continue
                            if bounced_email.startswith(("mailer-daemon@", "postmaster@")):
                                continue

                            contact = db.execute(
                                "SELECT id, bounce_count FROM contacts WHERE email = ? AND deleted_at IS NULL",
                                (bounced_email,)
                            ).fetchone()

                            if contact:
                                new_count = contact["bounce_count"] + 1
                                # Hard bounce or 3+ soft bounces -> mark as bounced
                                new_status = "bounced" if (bounce_type == "hard" or new_count >= 3) else "active"

                                db.execute("""
                                    UPDATE contacts SET
                                        status = ?,
                                        bounce_count = ?,
                                        last_bounce_at = datetime('now'),
                                        bounce_type = ?,
                                        updated_at = datetime('now')
                                    WHERE id = ?
                                """, (new_status, new_count, bounce_type, contact["id"]))

                                # Update send_log and campaign stats
                                # Find send_log entries for this contact that are 'delivered' (not already bounced)
                                sent_entries = db.execute("""
                                    SELECT sl.id, sl.campaign_id FROM send_log sl
                                    WHERE sl.contact_id = ? AND sl.status = 'delivered'
                                    ORDER BY sl.sent_at DESC
                                """, (contact["id"],)).fetchall()

                                for entry in sent_entries:
                                    # Mark send_log as bounced
                                    db.execute("""
                                        UPDATE send_log SET status = 'bounced',
                                            bounce_type = ?, error_message = ?
                                        WHERE id = ?
                                    """, (bounce_type, f"IMAP bounce: {bounce_type}", entry["id"]))

                                    # Update campaign counters
                                    db.execute("""
                                        UPDATE campaigns SET
                                            bounced = bounced + 1,
                                            delivered = CASE WHEN delivered > 0 THEN delivered - 1 ELSE 0 END
                                        WHERE id = ?
                                    """, (entry["campaign_id"],))

                                total_bounces += 1
                                logger.info(
                                    f"Bounce detected: {bounced_email} ({bounce_type}), "
                                    f"count={new_count}, status={new_status}, "
                                    f"campaigns_updated={len(sent_entries)}"
                                )

                        # Mark message as seen and move to trash/delete
                        imap.store(msg_id, '+FLAGS', '(\\Seen \\Deleted)')

                    except Exception as e:
                        logger.error(f"Error processing bounce message {msg_id}: {e}")
                        continue

                imap.expunge()  # Actually delete messages marked \Deleted
                imap.close()
                imap.logout()

                db.execute(
                    "UPDATE servers SET bounce_last_check = datetime('now') WHERE id = ?",
                    (server["id"],)
                )
                db.commit()

                if total_bounces > 0:
                    logger.info(f"Server {server['name']}: processed {total_bounces} bounces")

            except Exception as e:
                logger.error(f"Bounce check error for server {server['name']}: {e}")
                continue

    finally:
        db.close()

# Beat schedule
celery_app.conf.beat_schedule = {
    "reset-hourly-counters": {
        "task": "worker.tasks.reset_server_counters",
        "schedule": 3600.0,  # every hour
    },
    "reset-daily-counters": {
        "task": "worker.tasks.reset_daily_counters",
        "schedule": 86400.0,  # every day
    },
    "check-scheduled-campaigns": {
        "task": "worker.tasks.check_scheduled_campaigns",
        "schedule": 60.0,  # every minute
    },
    "check-bounces": {
        "task": "worker.tasks.check_bounces",
        "schedule": 300.0,  # every 5 minutes
    },
    "pool-bounce-check": {
        "task": "worker.pool_tasks.check_pool_bounces",
        "schedule": 900.0,  # every 15 minutes
    },
}