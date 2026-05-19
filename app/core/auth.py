"""
Authentication helpers.

Single-user system: credentials live in the `app_settings` table (key-value).
On first run (table empty), the password from .env is bootstrapped — bcrypt
hashed and stored. From then on, .env is ignored and the DB is the source
of truth. Username is fixed to 'admin' (per product decision).
"""
import bcrypt as _bcrypt
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.config import SECRET_KEY, ADMIN_PASSWORD, SESSION_MAX_AGE
from app.db.database import get_db

serializer = URLSafeTimedSerializer(SECRET_KEY)
COOKIE_NAME = "session_token"

# Username is fixed — single-user system. We only manage the password.
ADMIN_USERNAME = "admin"


def _hash_password(password: str) -> str:
    """Bcrypt-hash a password. Returns a string suitable for DB storage."""
    # bcrypt limits to 72 bytes — truncate explicitly so we never raise
    pw = password.encode("utf-8")[:72]
    return _bcrypt.hashpw(pw, _bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against bcrypt hash. Safe against malformed hashes."""
    if not stored_hash:
        return False
    pw = password.encode("utf-8")[:72]
    try:
        return _bcrypt.checkpw(pw, stored_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _get_setting(key: str) -> str | None:
    """Fetch a value from app_settings, or None if not present."""
    db = get_db()
    try:
        row = db.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None
    finally:
        db.close()


def _set_setting(key: str, value: str) -> None:
    """Upsert a value into app_settings."""
    db = get_db()
    try:
        db.execute("""
            INSERT INTO app_settings (key, value, updated_at) VALUES (?, ?, datetime('now'))
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=datetime('now')
        """, (key, value))
        db.commit()
    finally:
        db.close()


def _bootstrap_admin_password() -> str:
    """
    Ensure the password hash exists in DB. If missing (first run after
    upgrade or fresh install), seed it from ADMIN_PASSWORD env and
    return the new hash. Idempotent.
    """
    existing = _get_setting("admin_password_hash")
    if existing:
        return existing
    seed = ADMIN_PASSWORD or "admin"
    new_hash = _hash_password(seed)
    _set_setting("admin_password_hash", new_hash)
    return new_hash


def verify_login(username: str, password: str) -> bool:
    """Validate credentials against bcrypt hash stored in DB."""
    if username != ADMIN_USERNAME:
        return False
    stored_hash = _bootstrap_admin_password()
    return _verify_password(password, stored_hash)


def change_password(current_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change the admin password. Returns (ok, message_key).
    The 'message_key' is a translation key (resolved by the caller via t()),
    not a user-facing string. This keeps auth.py free of UI language concerns.
    Caller should already have verified the user is logged in.
    """
    if not new_password or len(new_password) < 8:
        return False, "profile_err_password_too_short"
    if new_password == current_password:
        return False, "profile_err_password_same"
    if not verify_login(ADMIN_USERNAME, current_password):
        return False, "profile_err_current_wrong"
    _set_setting("admin_password_hash", _hash_password(new_password))
    return True, "profile_msg_password_changed"


def create_session_token(username: str) -> str:
    """Create a signed session token."""
    return serializer.dumps({"user": username})


def get_current_user(request: Request) -> str | None:
    """Extract username from session cookie, or None."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("user")
    except (BadSignature, SignatureExpired):
        return None


def set_session_cookie(response: Response, token: str):
    """Set session cookie on response."""
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
    )


def clear_session_cookie(response: Response):
    """Remove session cookie."""
    response.delete_cookie(COOKIE_NAME)


def require_auth(request: Request) -> RedirectResponse | None:
    """Returns redirect to login if not authenticated, else None."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return None