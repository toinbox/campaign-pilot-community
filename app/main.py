import csv
import io
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from urllib.parse import unquote, quote
import hmac
import hashlib
import geoip2.database
import geoip2.errors
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import logging
from app.config import APP_NAME, WEB_HOST, WEB_PORT
import os as _os
GEOIP_PATH = _os.getenv("GEOIP_PATH", "/geoip/GeoLite2.mmdb")
from app.db.database import get_db, init_db
from app.core.auth import (
    verify_login, create_session_token, get_current_user,
    set_session_cookie, clear_session_cookie, require_auth,
    change_password,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME, lifespan=lifespan)

templates = Jinja2Templates(directory="app/templates")

# ── Timezone filter for templates ──
from zoneinfo import ZoneInfo
from datetime import datetime as _datetime

def _to_prague(dt_str):
    """Convert UTC datetime string to Europe/Prague localtime."""
    if not dt_str:
        return "–"
    try:
        dt = _datetime.fromisoformat(str(dt_str)).replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(ZoneInfo("Europe/Prague")).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(dt_str)

templates.env.filters["prague"] = _to_prague

# ── i18n: language detection middleware + global t() function for templates ──
# This setup means every template can use {{ t('key') }} and {{ lang }} without
# any per-endpoint changes. resolve_language() picks cookie -> app_settings ->
# Accept-Language -> 'cs'. Falls back to 'cs' if anything goes wrong.
from app.core.translations import (
    t as _t_fn, resolve_language, SUPPORTED_LANGS, LANG_NAMES,
    DEFAULT_LANG, LANG_COOKIE,
)
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Per-request language storage. Set by middleware before each request.
# ContextVar is the right tool here — avoids thread-local issues with async.
_current_lang: ContextVar[str] = ContextVar("_current_lang", default=DEFAULT_LANG)


class LanguageMiddleware(BaseHTTPMiddleware):
    """Resolve active language once per request and stash on request.state + ContextVar."""
    async def dispatch(self, request, call_next):
        try:
            lang = resolve_language(request)
        except Exception:
            lang = DEFAULT_LANG
        request.state.lang = lang
        token = _current_lang.set(lang)
        try:
            return await call_next(request)
        finally:
            _current_lang.reset(token)


app.add_middleware(LanguageMiddleware)


def _template_t(key: str) -> str:
    """Jinja2 global: {{ t('key') }}. Reads lang from ContextVar."""
    return _t_fn(key, _current_lang.get())


def _template_current_lang() -> str:
    """Jinja2 global: {{ current_lang() }} -> active lang code."""
    return _current_lang.get()


templates.env.globals["t"] = _template_t
templates.env.globals["current_lang"] = _template_current_lang
templates.env.globals["SUPPORTED_LANGS"] = SUPPORTED_LANGS
templates.env.globals["LANG_NAMES"] = LANG_NAMES

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception:
    pass


# ══════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if get_current_user(request):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_login(username, password):
        token = create_session_token(username)
        resp = RedirectResponse("/", status_code=302)
        set_session_cookie(resp, token)
        return resp
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "error": "Neplatné přihlašovací údaje",
    })


@app.get("/logout")
def logout(request: Request):
    resp = RedirectResponse("/login", status_code=302)
    clear_session_cookie(resp)
    return resp


# ══════════════════════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════════════════════

def _get_stored_user_language() -> str:
    """Read the persisted language preference from app_settings, or '' if none."""
    try:
        db = get_db()
        try:
            row = db.execute(
                "SELECT value FROM app_settings WHERE key='user_language'"
            ).fetchone()
            return row["value"] if row else ""
        finally:
            db.close()
    except Exception:
        return ""


def _set_stored_user_language(lang: str) -> None:
    """Persist the language preference to app_settings."""
    db = get_db()
    try:
        db.execute("""
            INSERT INTO app_settings (key, value, updated_at) VALUES ('user_language', ?, datetime('now'))
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=datetime('now')
        """, (lang,))
        db.commit()
    finally:
        db.close()


@app.post("/set-lang")
def set_lang(request: Request, lang: str = Form(...)):
    """
    Quick language switch via dropdown. Sets the cookie and redirects back.
    Does NOT persist to DB — for that, use the profile page.
    Anyone can call this (even unauthenticated) since language is UI-only.
    """
    target = request.headers.get("referer", "/")
    # Sanity-check the redirect target so we don't bounce off-site
    if not target.startswith("/") and not target.startswith(str(request.base_url)):
        target = "/"

    resp = RedirectResponse(target, status_code=302)
    if lang in SUPPORTED_LANGS:
        resp.set_cookie(
            LANG_COOKIE, lang,
            max_age=60 * 60 * 24 * 365,  # 1 year
            httponly=False,  # readable from JS for any future client-side use
            samesite="lax",
        )
    return resp


@app.get("/profile", response_class=HTMLResponse)
def profile_get(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    from app.config import DEMO_MODE
    return templates.TemplateResponse("auth/profile.html", {
        "request": request,
        "user": get_current_user(request),
        "message": None,
        "error": None,
        "demo_mode": DEMO_MODE,
        "stored_lang": _get_stored_user_language(),
    })


@app.post("/profile", response_class=HTMLResponse)
def profile_post(
    request: Request,
    current_password: str = Form(""),
    new_password: str = Form(""),
    new_password_confirm: str = Form(""),
    preferred_language: str = Form(""),
    action: str = Form("change_password"),
):
    auth = require_auth(request)
    if auth:
        return auth

    from app.config import DEMO_MODE
    from app.core.translations import t as _t

    # Helper: translate a key using the active request language
    def _msg(key: str) -> str:
        return _t(key, _current_lang.get())

    # ── Action: save language preference ──
    if action == "save_language":
        if preferred_language and preferred_language in SUPPORTED_LANGS:
            _set_stored_user_language(preferred_language)
            resp = RedirectResponse("/profile", status_code=302)
            # Also set cookie so change is immediate (DB read happens on next request)
            resp.set_cookie(
                LANG_COOKIE, preferred_language,
                max_age=60 * 60 * 24 * 365, httponly=False, samesite="lax",
            )
            return resp
        # Invalid language code — render with error
        return templates.TemplateResponse("auth/profile.html", {
            "request": request,
            "user": get_current_user(request),
            "message": None,
            "error": _msg("profile_err_invalid_lang"),
            "demo_mode": DEMO_MODE,
            "stored_lang": _get_stored_user_language(),
        })

    # ── Action: change password (default) ──
    # Defense-in-depth: even if the form is bypassed (curl, etc.), reject the request.
    if DEMO_MODE:
        return templates.TemplateResponse("auth/profile.html", {
            "request": request,
            "user": get_current_user(request),
            "message": None,
            "error": _msg("profile_err_demo_blocked"),
            "demo_mode": True,
            "stored_lang": _get_stored_user_language(),
        })

    if new_password != new_password_confirm:
        return templates.TemplateResponse("auth/profile.html", {
            "request": request,
            "user": get_current_user(request),
            "message": None,
            "error": _msg("profile_err_password_mismatch"),
            "demo_mode": False,
            "stored_lang": _get_stored_user_language(),
        })

    ok, msg_key = change_password(current_password, new_password)
    msg_text = _msg(msg_key)
    return templates.TemplateResponse("auth/profile.html", {
        "request": request,
        "user": get_current_user(request),
        "message": msg_text if ok else None,
        "error": msg_text if not ok else None,
        "demo_mode": False,
        "stored_lang": _get_stored_user_language(),
    })


# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    auth = require_auth(request)
    if auth:
        return auth

    db = get_db()
    try:
        stats = {
            "total_contacts": db.execute("SELECT COUNT(*) FROM contacts WHERE deleted_at IS NULL").fetchone()[0],
            "active_contacts": db.execute("SELECT COUNT(*) FROM contacts WHERE status='active' AND deleted_at IS NULL").fetchone()[0],
            "bounced_contacts": db.execute("SELECT COUNT(*) FROM contacts WHERE status='bounced' AND deleted_at IS NULL").fetchone()[0],
            "total_campaigns": db.execute("SELECT COUNT(*) FROM campaigns WHERE deleted_at IS NULL").fetchone()[0],
            "running_campaigns": db.execute("SELECT COUNT(*) FROM campaigns WHERE status='running' AND deleted_at IS NULL").fetchone()[0],
            "blocked_domains": db.execute("SELECT COUNT(*) FROM destination_limits WHERE blocked=1").fetchone()[0],
            "sent_today": db.execute("""
                SELECT COUNT(*) FROM send_log
                WHERE sent_at >= date('now') AND status IN ('delivered','sent','sending','bounced')
            """).fetchone()[0],
            "bounced_today": db.execute("""
                SELECT COUNT(*) FROM send_log
                WHERE sent_at >= date('now') AND status = 'bounced'
            """).fetchone()[0],
            "total_servers": db.execute("SELECT COUNT(*) FROM servers WHERE deleted_at IS NULL").fetchone()[0],
            "active_servers": db.execute("SELECT COUNT(*) FROM servers WHERE status='active' AND deleted_at IS NULL").fetchone()[0],
        }
        recent_campaigns = db.execute(
            "SELECT * FROM campaigns WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 10"
        ).fetchall()

        # Servers with real sent counts from send_log (Prague timezone)
        servers = db.execute("""
            SELECT s.*,
                COALESCE(hour_counts.sent_hour, 0) as real_sent_hour,
                COALESCE(day_counts.sent_day, 0) as real_sent_day
            FROM servers s
            LEFT JOIN (
                SELECT server_id, COUNT(*) as sent_hour FROM send_log
                WHERE sent_at >= datetime('now', '-1 hour')
                GROUP BY server_id
            ) hour_counts ON s.id = hour_counts.server_id
            LEFT JOIN (
                SELECT server_id, COUNT(*) as sent_day FROM send_log
                WHERE date(sent_at, 'localtime') >= date('now', 'localtime')
                GROUP BY server_id
            ) day_counts ON s.id = day_counts.server_id
            WHERE s.deleted_at IS NULL
            ORDER BY s.name
        """).fetchall()
    finally:
        db.close()

    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "stats": stats,
        "recent_campaigns": recent_campaigns,
        "servers": servers,
        "running_campaigns": stats["running_campaigns"],
        "blocked_domains": stats["blocked_domains"],
    })


# ══════════════════════════════════════════════════════════
# SERVERS
# ══════════════════════════════════════════════════════════

@app.get("/servers", response_class=HTMLResponse)
def servers_list(request: Request, flash: str = "", flash_type: str = "success"):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        servers = db.execute("SELECT * FROM servers WHERE deleted_at IS NULL ORDER BY name").fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("servers/list.html", {
        "request": request, "servers": servers,
        "flash_message": flash, "flash_type": flash_type,
    })


@app.get("/servers/new", response_class=HTMLResponse)
def server_new_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    return templates.TemplateResponse("servers/form.html", {"request": request, "server": None})


@app.post("/servers/new")
async def server_create(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    f = await request.form()
    db = get_db()
    try:
        db.execute("""
            INSERT INTO servers (name, smtp_host, smtp_port, smtp_user, smtp_password, use_tls,
                from_email, from_name, tracking_domain, hourly_limit, daily_limit, weight, status,
                bounce_check_enabled, bounce_imap_host, bounce_imap_port,
                bounce_imap_user, bounce_imap_password, bounce_imap_ssl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f.get("name"), f.get("smtp_host"), int(f.get("smtp_port", 587)),
            f.get("smtp_user"), f.get("smtp_password"),
            1 if f.get("use_tls") else 0,
            f.get("from_email"), f.get("from_name", ""),
            (f.get("tracking_domain") or "").strip().rstrip("/"),
            int(f.get("hourly_limit", 100)), int(f.get("daily_limit", 500)),
            int(f.get("weight", 50)), f.get("status", "active"),
            1 if f.get("bounce_check_enabled") else 0,
            f.get("bounce_imap_host", ""), int(f.get("bounce_imap_port", 993)),
            f.get("bounce_imap_user", ""), f.get("bounce_imap_password", ""),
            1 if f.get("bounce_imap_ssl") else 0,
        ))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/servers", status_code=302)


@app.get("/servers/{server_id}/edit", response_class=HTMLResponse)
def server_edit_form(request: Request, server_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        server = db.execute("SELECT * FROM servers WHERE id=? AND deleted_at IS NULL", (server_id,)).fetchone()
    finally:
        db.close()
    if not server:
        return RedirectResponse("/servers", status_code=302)
    return templates.TemplateResponse("servers/form.html", {"request": request, "server": server})


@app.post("/servers/{server_id}/edit")
async def server_update(request: Request, server_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    f = await request.form()
    db = get_db()
    try:
        db.execute("""
            UPDATE servers SET name=?, smtp_host=?, smtp_port=?, smtp_user=?, smtp_password=?,
                use_tls=?, from_email=?, from_name=?, tracking_domain=?,
                hourly_limit=?, daily_limit=?, weight=?,
                status=?, bounce_check_enabled=?, bounce_imap_host=?, bounce_imap_port=?,
                bounce_imap_user=?, bounce_imap_password=?, bounce_imap_ssl=?,
                updated_at=datetime('now')
            WHERE id=? AND deleted_at IS NULL
        """, (
            f.get("name"), f.get("smtp_host"), int(f.get("smtp_port", 587)),
            f.get("smtp_user"), f.get("smtp_password"),
            1 if f.get("use_tls") else 0,
            f.get("from_email"), f.get("from_name", ""),
            (f.get("tracking_domain") or "").strip().rstrip("/"),
            int(f.get("hourly_limit", 100)), int(f.get("daily_limit", 500)),
            int(f.get("weight", 50)), f.get("status", "active"),
            1 if f.get("bounce_check_enabled") else 0,
            f.get("bounce_imap_host", ""), int(f.get("bounce_imap_port", 993)),
            f.get("bounce_imap_user", ""), f.get("bounce_imap_password", ""),
            1 if f.get("bounce_imap_ssl") else 0,
            server_id,
        ))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/servers", status_code=302)


@app.post("/servers/{server_id}/delete")
def server_delete(request: Request, server_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("UPDATE servers SET deleted_at=datetime('now') WHERE id=?", (server_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/servers", status_code=302)


# ══════════════════════════════════════════════════════════
# CONTACTS
# ══════════════════════════════════════════════════════════

@app.get("/contacts", response_class=HTMLResponse)
def contacts_list(request: Request, search: str = "", status: str = "", list_id: str = "", page: int = 1, flash: str = ""):
    auth = require_auth(request)
    if auth:
        return auth

    per_page = 50
    db = get_db()
    try:
        where = ["c.deleted_at IS NULL"]
        params = []
        if search:
            where.append("(c.email LIKE ? OR c.first_name LIKE ? OR c.last_name LIKE ?)")
            params.extend([f"%{search}%"] * 3)
        if status:
            where.append("c.status = ?")
            params.append(status)
        list_id_int = int(list_id) if list_id and list_id.isdigit() else 0
        if list_id_int:
            where.append("c.id IN (SELECT contact_id FROM contact_list_members WHERE list_id=?)")
            params.append(list_id_int)

        where_sql = " AND ".join(where)
        total = db.execute(f"SELECT COUNT(*) FROM contacts c WHERE {where_sql}", params).fetchone()[0]
        total_pages = max(1, (total + per_page - 1) // per_page)

        contacts = db.execute(f"""
            SELECT c.*,
                GROUP_CONCAT(DISTINCT cl.name) as list_names,
                COUNT(DISTINCT CASE WHEN sl.opened_at IS NOT NULL THEN sl.id END) as open_count,
                COUNT(DISTINCT CASE WHEN sl.clicked_at IS NOT NULL THEN sl.id END) as click_count
            FROM contacts c
            LEFT JOIN contact_list_members clm ON c.id = clm.contact_id
            LEFT JOIN contact_lists cl ON clm.list_id = cl.id AND cl.deleted_at IS NULL
            LEFT JOIN send_log sl ON c.id = sl.contact_id
            WHERE {where_sql}
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        """, params + [per_page, (page - 1) * per_page]).fetchall()
        all_lists = db.execute("SELECT id, name FROM contact_lists WHERE deleted_at IS NULL ORDER BY name").fetchall()
    finally:
        db.close()

    return templates.TemplateResponse("contacts/list.html", {
        "request": request,
        "contacts": contacts,
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "search": search,
        "filter_status": status,
        "filter_list_id": list_id_int,
        "flash_message": flash,
        "contact_lists": all_lists,
    })


@app.get("/contacts/new", response_class=HTMLResponse)
def contact_new_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        lists = db.execute("SELECT * FROM contact_lists WHERE deleted_at IS NULL ORDER BY name").fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("contacts/form.html", {
        "request": request, "contact": None, "lists": lists, "contact_list_ids": [],
    })


@app.post("/contacts/new")
async def contact_create(request: Request):
    auth = require_auth(request)
    if auth:
        return auth

    form_data = await request.form()
    email = form_data.get("email", "").strip().lower()
    first_name = form_data.get("first_name", "").strip()
    last_name = form_data.get("last_name", "").strip()
    company = form_data.get("company", "").strip()
    tags = form_data.get("tags", "").strip()
    list_ids = form_data.getlist("list_ids")

    db = get_db()
    try:
        # Check if soft-deleted contact exists — restore instead of insert
        existing = db.execute(
            "SELECT id FROM contacts WHERE email=?", (email,)
        ).fetchone()

        if existing:
            # Restore soft deleted contact or update existing
            db.execute("""
                UPDATE contacts SET
                    first_name=?, last_name=?, company=?, tags=?,
                    deleted_at=NULL, updated_at=datetime('now'), status='active'
                WHERE email=?
            """, (first_name, last_name, company, tags, email))
        else:
            db.execute("""
                INSERT INTO contacts (email, first_name, last_name, company, tags, source)
                VALUES (?, ?, ?, ?, ?, 'manual')
            """, (email, first_name, last_name, company, tags))
        db.commit()

        # Assign to lists
        if list_ids:
            contact_row = db.execute("SELECT id FROM contacts WHERE email=?", (email,)).fetchone()
            if contact_row:
                contact_id = contact_row[0]
                for lid in list_ids:
                    if lid:
                        db.execute(
                            "INSERT OR IGNORE INTO contact_list_members (contact_id, list_id) VALUES (?, ?)",
                            (contact_id, int(lid))
                        )
                db.commit()
    finally:
        db.close()
    return RedirectResponse("/contacts", status_code=302)


@app.get("/contacts/{contact_id}/edit", response_class=HTMLResponse)
def contact_edit_form(request: Request, contact_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        contact = db.execute("SELECT * FROM contacts WHERE id=? AND deleted_at IS NULL", (contact_id,)).fetchone()
        lists = db.execute("SELECT * FROM contact_lists WHERE deleted_at IS NULL ORDER BY name").fetchall()
        contact_list_ids = [r[0] for r in db.execute(
            "SELECT list_id FROM contact_list_members WHERE contact_id=?", (contact_id,)
        ).fetchall()]
    finally:
        db.close()
    if not contact:
        return RedirectResponse("/contacts", status_code=302)
    return templates.TemplateResponse("contacts/form.html", {
        "request": request, "contact": contact, "lists": lists, "contact_list_ids": contact_list_ids,
    })


@app.post("/contacts/{contact_id}/edit")
async def contact_update(request: Request, contact_id: int):
    auth = require_auth(request)
    if auth:
        return auth

    form_data = await request.form()
    email = form_data.get("email", "").strip().lower()
    first_name = form_data.get("first_name", "").strip()
    last_name = form_data.get("last_name", "").strip()
    company = form_data.get("company", "").strip()
    tags = form_data.get("tags", "").strip()
    status = form_data.get("status", "active")
    list_ids = form_data.getlist("list_ids")

    db = get_db()
    try:
        db.execute("""
            UPDATE contacts SET email=?, first_name=?, last_name=?, company=?, tags=?,
                status=?, updated_at=datetime('now')
            WHERE id=? AND deleted_at IS NULL
        """, (email, first_name, last_name, company, tags, status, contact_id))

        # Update list memberships - remove old, add new
        db.execute("DELETE FROM contact_list_members WHERE contact_id=?", (contact_id,))
        if list_ids:
            for lid in list_ids:
                if lid:
                    db.execute(
                        "INSERT OR IGNORE INTO contact_list_members (contact_id, list_id) VALUES (?, ?)",
                        (contact_id, int(lid))
                    )
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/contacts", status_code=302)


@app.post("/contacts/{contact_id}/delete")
def contact_delete(request: Request, contact_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("DELETE FROM contact_list_members WHERE contact_id=?", (contact_id,))
        db.execute("""DELETE FROM email_tracking_tokens WHERE send_log_id IN (
            SELECT id FROM send_log WHERE contact_id=?)""", (contact_id,))
        db.execute("DELETE FROM send_log WHERE contact_id=?", (contact_id,))
        db.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/contacts", status_code=302)


@app.get("/contacts/import", response_class=HTMLResponse)
def contacts_import_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        lists = db.execute("SELECT * FROM contact_lists WHERE deleted_at IS NULL ORDER BY name").fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("contacts/import.html", {"request": request, "lists": lists})


@app.post("/contacts/import")
async def contacts_import_submit(request: Request):
    auth = require_auth(request)
    if auth:
        return auth

    form_data = await request.form()
    csv_file = form_data.get("csv_file")
    list_ids = form_data.getlist("list_ids")
    delimiter = form_data.get("delimiter", ",")
    skip_duplicates = form_data.get("skip_duplicates", "0")

    content = await csv_file.read()
    text = content.decode("utf-8-sig", errors="ignore")

    if delimiter == "\\t":
        delimiter = "\t"

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    db = get_db()
    imported = 0
    skipped = 0
    restored = 0
    try:
        for row in reader:
            email = row.get("email", "").strip().lower()
            if not email or "@" not in email:
                skipped += 1
                continue

            first_name = row.get("first_name", "").strip()
            last_name = row.get("last_name", "").strip()
            company = row.get("company", "").strip()
            tags = row.get("tags", "").strip()

            try:
                # Check if contact exists (including soft-deleted)
                existing = db.execute("SELECT id, deleted_at, status FROM contacts WHERE email=?", (email,)).fetchone()

                if existing and existing["deleted_at"]:
                    # Restore soft-deleted contact
                    db.execute("""
                        UPDATE contacts SET deleted_at=NULL, status='active',
                            first_name=?, last_name=?, company=?, tags=?,
                            bounce_count=0, bounce_type=NULL,
                            source='import', updated_at=datetime('now')
                        WHERE id=?
                    """, (first_name, last_name, company, tags, existing["id"]))
                    restored += 1
                    contact_id = existing["id"]

                elif existing:
                    # Already exists and active - skip
                    skipped += 1
                    contact_id = existing["id"]
                else:
                    # New contact
                    db.execute("""
                        INSERT INTO contacts (email, first_name, last_name, company, tags, source)
                        VALUES (?, ?, ?, ?, ?, 'import')
                    """, (email, first_name, last_name, company, tags))
                    contact_id = db.execute("SELECT id FROM contacts WHERE email=?", (email,)).fetchone()[0]
                    imported += 1

                # Assign to selected lists (always, even for existing contacts)
                if list_ids and contact_id:
                    for lid in list_ids:
                        if lid:
                            db.execute(
                                "INSERT OR IGNORE INTO contact_list_members (contact_id, list_id) VALUES (?, ?)",
                                (contact_id, int(lid))
                            )
            except Exception as e:
                skipped += 1

        db.commit()
    finally:
        db.close()

    parts = []
    if imported:
        parts.append(f"importováno {imported} nových")
    if restored:
        parts.append(f"obnoveno {restored} smazaných")
    if skipped:
        parts.append(f"přeskočeno {skipped} existujících")
    flash_msg = ", ".join(parts).capitalize() if parts else "Žádné kontakty k importu"

    return RedirectResponse(f"/contacts?flash={flash_msg}", status_code=302)


# ══════════════════════════════════════════════════════════
# CONTACT LISTS
# ══════════════════════════════════════════════════════════

@app.get("/lists", response_class=HTMLResponse)
def lists_page(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        lists = db.execute("""
            SELECT cl.*,
                COUNT(CASE WHEN c.deleted_at IS NULL AND c.status = 'active' THEN 1 END) as member_count
            FROM contact_lists cl
            LEFT JOIN contact_list_members clm ON cl.id = clm.list_id
            LEFT JOIN contacts c ON clm.contact_id = c.id
            WHERE cl.deleted_at IS NULL
            GROUP BY cl.id
            ORDER BY cl.created_at DESC
        """).fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("contacts/lists.html", {"request": request, "lists": lists})


@app.get("/lists/new", response_class=HTMLResponse)
def list_new_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    return templates.TemplateResponse("contacts/list_form.html", {"request": request, "list_item": None})


@app.get("/lists/{list_id}/export")
def list_export(request: Request, list_id: int, mode: str = "clean"):
    """
    Export list contacts as CSV — clean import-ready format.
    Always: email, first_name, last_name, company, tags (no status, source, etc.)
    mode=clean (active only), mode=all, mode=bounced, mode=unsubscribed
    """
    auth = require_auth(request)
    if auth:
        return auth

    db = get_db()
    try:
        list_info = db.execute("SELECT name FROM contact_lists WHERE id=? AND deleted_at IS NULL", (list_id,)).fetchone()
        if not list_info:
            return RedirectResponse("/lists", status_code=302)

        if mode == "clean":
            where = "AND c.status = 'active'"
        elif mode == "bounced":
            where = "AND c.status = 'bounced'"
        elif mode == "unsubscribed":
            where = "AND c.status = 'unsubscribed'"
        else:
            where = ""

        contacts = db.execute(f"""
            SELECT c.email, c.first_name, c.last_name, c.company, c.tags
            FROM contacts c
            JOIN contact_list_members clm ON c.id = clm.contact_id
            WHERE clm.list_id = ? AND c.deleted_at IS NULL {where}
            ORDER BY c.email
        """, (list_id,)).fetchall()
    finally:
        db.close()

    # Always clean format — email + identity fields only, no metadata
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["email", "first_name", "last_name", "company", "tags"])
    for c in contacts:
        writer.writerow([c["email"], c["first_name"], c["last_name"], c["company"], c["tags"]])

    from fastapi.responses import StreamingResponse
    content = output.getvalue()
    safe_name = list_info["name"].replace(" ", "_").replace("/", "")
    filename = f"{safe_name}_{mode}_{datetime.now().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/contacts/export")
def contacts_export(
    request: Request,
    mode: str = "clean",
    list_id: int | None = None,
    status: str = "",
    search: str = "",
):
    """
    Export contacts as CSV — always clean import-ready format.
    Columns: email, first_name, last_name, company, tags  (NO status, source, etc.)

    Filters mirror /contacts UI:
      - list_id: only contacts in this list
      - status: only contacts with this status (overrides mode)
      - search: text search in email/name/company
      - mode: status shortcut (clean=active, bounced, unsubscribed, all)
    """
    auth = require_auth(request)
    if auth:
        return auth

    # Resolve effective status filter — explicit `status` wins over `mode`
    effective_status = status.strip()
    if not effective_status:
        if mode == "clean":
            effective_status = "active"
        elif mode in ("bounced", "unsubscribed"):
            effective_status = mode
        # mode == "all" or anything else → no status filter

    db = get_db()
    try:
        list_name = None
        params: list = []
        joins = ""
        wheres = ["c.deleted_at IS NULL"]

        if list_id is not None:
            joins = "JOIN contact_list_members clm ON c.id = clm.contact_id"
            wheres.append("clm.list_id = ?")
            params.append(list_id)

            row = db.execute(
                "SELECT name FROM contact_lists WHERE id=? AND deleted_at IS NULL",
                (list_id,),
            ).fetchone()
            if row:
                list_name = row["name"]

        if effective_status:
            wheres.append("c.status = ?")
            params.append(effective_status)

        if search:
            wheres.append("(c.email LIKE ? OR c.first_name LIKE ? OR c.last_name LIKE ? OR c.company LIKE ?)")
            like = f"%{search}%"
            params.extend([like, like, like, like])

        where_sql = " AND ".join(wheres)
        sql = f"""
            SELECT c.email, c.first_name, c.last_name, c.company, c.tags
            FROM contacts c
            {joins}
            WHERE {where_sql}
            ORDER BY c.email
        """
        contacts = db.execute(sql, params).fetchall()
    finally:
        db.close()

    # Always clean format — no status, no source, no metadata
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["email", "first_name", "last_name", "company", "tags"])
    for c in contacts:
        writer.writerow([c["email"], c["first_name"], c["last_name"], c["company"], c["tags"]])

    from fastapi.responses import StreamingResponse

    # Build descriptive filename: list_status_date.csv
    parts = []
    if list_name:
        safe_list = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in list_name)
        parts.append(safe_list)
    else:
        parts.append("contacts")
    parts.append(effective_status or "all")
    parts.append(datetime.now().strftime("%Y%m%d"))
    filename = "_".join(parts) + ".csv"

    content = output.getvalue()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/lists/new")
def list_create(request: Request, name: str = Form(...), description: str = Form("")):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("INSERT INTO contact_lists (name, description) VALUES (?, ?)", (name, description))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/lists", status_code=302)


@app.post("/lists/{list_id}/delete")
async def list_delete(request: Request, list_id: int):
    auth = require_auth(request)
    if auth:
        return auth

    f = await request.form()
    delete_contacts = f.get("delete_contacts", "0") == "1"

    db = get_db()
    try:
        if delete_contacts:
            # Soft delete contacts that are only in this list
            only_in_this = [r[0] for r in db.execute("""
                SELECT contact_id FROM contact_list_members
                WHERE list_id = ?
                AND contact_id NOT IN (
                    SELECT contact_id FROM contact_list_members WHERE list_id != ?
                )
            """, (list_id, list_id)).fetchall()]

            if only_in_this:
                ph = ",".join(["?"] * len(only_in_this))
                # Soft delete contacts instead of hard delete to avoid FK issues
                db.execute(f"UPDATE contacts SET deleted_at=datetime('now') WHERE id IN ({ph})", only_in_this)

        # Remove memberships and soft delete the list
        db.execute("DELETE FROM contact_list_members WHERE list_id=?", (list_id,))
        db.execute("UPDATE campaigns SET list_id=NULL WHERE list_id=?", (list_id,))
        db.execute("UPDATE contact_lists SET deleted_at=datetime('now') WHERE id=?", (list_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/lists", status_code=302)

@app.post("/contacts/bulk-delete")
async def contacts_bulk_delete(request: Request):
    """Delete multiple contacts at once."""
    auth = require_auth(request)
    if auth:
        return auth

    f = await request.form()
    contact_ids = f.getlist("contact_ids")
    delete_mode = f.get("delete_mode", "selected")

    db = get_db()
    deleted = 0
    try:
        if delete_mode == "selected" and contact_ids:
            placeholders = ",".join(["?"] * len(contact_ids))
            ids = [int(cid) for cid in contact_ids if cid]
            db.execute(f"DELETE FROM contact_list_members WHERE contact_id IN ({placeholders})", ids)
            db.execute(f"DELETE FROM email_tracking_tokens WHERE send_log_id IN (SELECT id FROM send_log WHERE contact_id IN ({placeholders}))", ids)
            db.execute(f"DELETE FROM send_log WHERE contact_id IN ({placeholders})", ids)
            deleted = db.execute(f"SELECT COUNT(*) FROM contacts WHERE id IN ({placeholders})", ids).fetchone()[0]
            db.execute(f"DELETE FROM contacts WHERE id IN ({placeholders})", ids)

        elif delete_mode == "bounced":
            deleted = db.execute("SELECT COUNT(*) FROM contacts WHERE status='bounced' AND deleted_at IS NULL").fetchone()[0]
            db.execute("DELETE FROM contact_list_members WHERE contact_id IN (SELECT id FROM contacts WHERE status='bounced')")
            db.execute("DELETE FROM email_tracking_tokens WHERE send_log_id IN (SELECT id FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='bounced'))")
            db.execute("DELETE FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='bounced')")
            db.execute("DELETE FROM contacts WHERE status='bounced'")

        elif delete_mode == "unsubscribed":
            deleted = db.execute("SELECT COUNT(*) FROM contacts WHERE status='unsubscribed' AND deleted_at IS NULL").fetchone()[0]
            db.execute("DELETE FROM contact_list_members WHERE contact_id IN (SELECT id FROM contacts WHERE status='unsubscribed')")
            db.execute("DELETE FROM email_tracking_tokens WHERE send_log_id IN (SELECT id FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='unsubscribed'))")
            db.execute("DELETE FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='unsubscribed')")
            db.execute("DELETE FROM contacts WHERE status='unsubscribed'")

        elif delete_mode == "invalid":
            deleted = db.execute("SELECT COUNT(*) FROM contacts WHERE status='invalid' AND deleted_at IS NULL").fetchone()[0]
            db.execute("DELETE FROM contact_list_members WHERE contact_id IN (SELECT id FROM contacts WHERE status='invalid')")
            db.execute("DELETE FROM email_tracking_tokens WHERE send_log_id IN (SELECT id FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='invalid'))")
            db.execute("DELETE FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE status='invalid')")
            db.execute("DELETE FROM contacts WHERE status='invalid'")

        elif delete_mode == "all":
            deleted = db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            db.execute("DELETE FROM contact_list_members")
            db.execute("DELETE FROM email_tracking_tokens")
            db.execute("DELETE FROM send_log")
            db.execute("DELETE FROM contacts")

        elif delete_mode == "all_filtered":
            search = f.get("filter_search", "")
            status = f.get("filter_status", "")
            where = ["1=1"]
            params = []
            if search:
                where.append("(email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)")
                params.extend([f"%{search}%"] * 3)
            if status:
                where.append("status = ?")
                params.append(status)
            where_sql = " AND ".join(where)

            deleted = db.execute(f"SELECT COUNT(*) FROM contacts WHERE {where_sql}", params).fetchone()[0]
            db.execute(f"DELETE FROM contact_list_members WHERE contact_id IN (SELECT id FROM contacts WHERE {where_sql})", params)
            db.execute(f"DELETE FROM email_tracking_tokens WHERE send_log_id IN (SELECT id FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE {where_sql}))", params)
            db.execute(f"DELETE FROM send_log WHERE contact_id IN (SELECT id FROM contacts WHERE {where_sql})", params)
            db.execute(f"DELETE FROM contacts WHERE {where_sql}", params)

        db.commit()
    finally:
        db.close()

    return RedirectResponse(f"/contacts?flash=Smazáno {deleted} kontaktů", status_code=302)


# ══════════════════════════════════════════════════════════
# EMAIL TEMPLATES
# ══════════════════════════════════════════════════════════

@app.get("/templates", response_class=HTMLResponse)
def templates_list(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        tmpls = db.execute("SELECT * FROM email_templates WHERE deleted_at IS NULL ORDER BY updated_at DESC").fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("email_templates/list.html", {"request": request, "templates_list": tmpls})


@app.get("/templates/new", response_class=HTMLResponse)
def template_new_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        layouts = db.execute("SELECT * FROM layouts WHERE deleted_at IS NULL").fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("email_templates/form.html", {
        "request": request, "template": None, "layouts": layouts
    })


@app.post("/templates/new")
def template_create(
    request: Request,
    name: str = Form(...),
    subject: str = Form(""),
    preheader: str = Form(""),
    html_body: str = Form(""),
    text_body: str = Form(""),
):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("""
            INSERT INTO email_templates (name, subject, preheader, html_body, text_body)
            VALUES (?, ?, ?, ?, ?)
        """, (name, subject, preheader, html_body, text_body))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/templates", status_code=302)


@app.get("/templates/{template_id}/edit", response_class=HTMLResponse)
def template_edit_form(request: Request, template_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        tmpl = db.execute("SELECT * FROM email_templates WHERE id=? AND deleted_at IS NULL", (template_id,)).fetchone()
        layouts = db.execute("SELECT * FROM layouts WHERE deleted_at IS NULL").fetchall()
    finally:
        db.close()
    if not tmpl:
        return RedirectResponse("/templates", status_code=302)
    return templates.TemplateResponse("email_templates/form.html", {
        "request": request, "template": tmpl, "layouts": layouts
    })


@app.post("/templates/{template_id}/edit")
def template_update(
    request: Request,
    template_id: int,
    name: str = Form(...),
    subject: str = Form(""),
    preheader: str = Form(""),
    html_body: str = Form(""),
    text_body: str = Form(""),
):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        # Save version before update
        old = db.execute("SELECT * FROM email_templates WHERE id=?", (template_id,)).fetchone()
        if old:
            ver_num = db.execute(
                "SELECT COALESCE(MAX(version_number),0)+1 FROM template_versions WHERE template_id=?",
                (template_id,)
            ).fetchone()[0]
            db.execute("""
                INSERT INTO template_versions (template_id, version_number, subject, html_body, text_body)
                VALUES (?, ?, ?, ?, ?)
            """, (template_id, ver_num, old["subject"], old["html_body"], old["text_body"]))

        db.execute("""
            UPDATE email_templates SET name=?, subject=?, preheader=?, html_body=?, text_body=?,
                updated_at=datetime('now')
            WHERE id=? AND deleted_at IS NULL
        """, (name, subject, preheader, html_body, text_body, template_id))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/templates", status_code=302)


@app.post("/templates/{template_id}/delete")
def template_delete(request: Request, template_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("UPDATE email_templates SET deleted_at=datetime('now') WHERE id=?", (template_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/templates", status_code=302)


@app.post("/templates/{template_id}/duplicate")
def template_duplicate(request: Request, template_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        tmpl = db.execute("SELECT * FROM email_templates WHERE id=? AND deleted_at IS NULL", (template_id,)).fetchone()
        if tmpl:
            db.execute("""
                INSERT INTO email_templates (name, layout_id, subject, content_json, html_body, text_body, variables)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f"{tmpl['name']} (kopie)", tmpl["layout_id"], tmpl["subject"],
                  tmpl["content_json"], tmpl["html_body"], tmpl["text_body"], tmpl["variables"]))
            db.commit()
    finally:
        db.close()
    return RedirectResponse("/templates", status_code=302)


# ══════════════════════════════════════════════════════════
# CAMPAIGNS (basic CRUD)
# ══════════════════════════════════════════════════════════

@app.get("/campaigns", response_class=HTMLResponse)
def campaigns_list(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaigns = db.execute(
            "SELECT * FROM campaigns WHERE deleted_at IS NULL ORDER BY created_at DESC"
        ).fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("campaigns/list.html", {"request": request, "campaigns": campaigns})


@app.get("/campaigns/new", response_class=HTMLResponse)
def campaign_new_form(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        tmpls = db.execute("SELECT id, name FROM email_templates WHERE deleted_at IS NULL").fetchall()
        lists = db.execute("SELECT id, name FROM contact_lists WHERE deleted_at IS NULL").fetchall()
        # Need status + smtp_host for the form template to render server cards
        servers = db.execute(
            "SELECT id, name, status, smtp_host FROM servers "
            "WHERE deleted_at IS NULL AND status IN ('active','warmup')"
        ).fetchall()
    finally:
        db.close()
    return templates.TemplateResponse("campaigns/form.html", {
        "request": request, "campaign": None,
        "templates_list": tmpls, "lists": lists, "servers": servers,
    })


@app.post("/campaigns/new")
def campaign_create(
    request: Request,
    name: str = Form(...),
    template_id: int = Form(...),
    list_id: int = Form(...),
    throttle_total: int = Form(100),
    throttle_window_minutes: int = Form(60),
    throttle_interval_min: float = Form(3.0),
    throttle_interval_max: float = Form(7.0),
    server_rotation_mode: str = Form("round_robin"),
    server_batch_size: int = Form(50),
    server_ids: str = Form(""),
    target_country: str = Form(""),
):
    auth = require_auth(request)
    if auth:
        return auth

    db = get_db()
    try:
        # Count recipients (apply country filter if set)
        if target_country and target_country != "OTHER":
            total = db.execute("""
                SELECT COUNT(DISTINCT c.id) FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                    AND c.geo_country_code = ?
            """, (list_id, target_country)).fetchone()[0]
        elif target_country == "OTHER":
            total = db.execute("""
                SELECT COUNT(DISTINCT c.id) FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
                    AND c.geo_country_code NOT IN ('CZ','SK','DE','AT','PL','HU')
                    AND c.geo_country_code != ''
            """, (list_id,)).fetchone()[0]
        else:
            total = db.execute("""
                SELECT COUNT(DISTINCT c.id) FROM contacts c
                JOIN contact_list_members clm ON c.id = clm.contact_id
                WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
            """, (list_id,)).fetchone()[0]

        cursor = db.execute("""
            INSERT INTO campaigns (name, template_id, list_id, throttle_total,
                throttle_window_minutes, throttle_interval_min, throttle_interval_max,
                server_rotation_mode, server_batch_size, total_recipients, target_country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, template_id, list_id, throttle_total, throttle_window_minutes,
              throttle_interval_min, throttle_interval_max, server_rotation_mode,
              server_batch_size, total, target_country))

        campaign_id = cursor.lastrowid

        # Link servers
        if server_ids:
            for i, sid in enumerate(server_ids.split(",")):
                if sid.strip():
                    db.execute(
                        "INSERT INTO campaign_servers (campaign_id, server_id, priority) VALUES (?, ?, ?)",
                        (campaign_id, int(sid.strip()), i)
                    )

        db.commit()
    finally:
        db.close()
    return RedirectResponse("/campaigns", status_code=302)


@app.post("/campaigns/{campaign_id}/delete")
def campaign_delete(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("UPDATE campaigns SET deleted_at=datetime('now') WHERE id=?", (campaign_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/campaigns", status_code=302)


@app.get("/campaigns/{campaign_id}", response_class=HTMLResponse)
def campaign_detail(request: Request, campaign_id: int, flash: str = "", flash_type: str = "success"):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaign = db.execute("SELECT * FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)).fetchone()
        if not campaign:
            return RedirectResponse("/campaigns", status_code=302)

        # Recalculate live stats directly from send_log (avoids WAL read snapshot issue)
        live_stats = db.execute("""
            SELECT
                COUNT(*) as sent_count,
                SUM(CASE WHEN status IN ('delivered','opened','clicked') THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'bounced' THEN 1 ELSE 0 END) as bounced,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
                SUM(CASE WHEN clicked_at IS NOT NULL THEN 1 ELSE 0 END) as clicked
            FROM send_log WHERE campaign_id = ?
        """, (campaign_id,)).fetchone()

        # Merge live stats into campaign dict
        campaign = dict(campaign)
        if live_stats and live_stats["sent_count"]:
            campaign["sent_count"] = live_stats["sent_count"]
            campaign["delivered"] = live_stats["delivered"] or 0
            # Use max of send_log bounced and campaigns.bounced
            # IMAP bounces update campaigns.bounced but not send_log
            campaign["bounced"] = max(live_stats["bounced"] or 0, campaign["bounced"] or 0)
            campaign["failed"] = live_stats["failed"] or 0
            campaign["opened"] = live_stats["opened"] or 0
            campaign["clicked"] = live_stats["clicked"] or 0
            # blocked_count comes from campaigns table directly
            campaign["blocked_count"] = campaign.get("blocked_count") or 0

        # Get template info
        tmpl = db.execute("SELECT name, subject FROM email_templates WHERE id=?", (campaign["template_id"],)).fetchone()

        # Get list info
        clist = db.execute("SELECT name FROM contact_lists WHERE id=?", (campaign["list_id"],)).fetchone()

        # Get assigned servers with real send counts for THIS campaign
        servers = db.execute("""
            SELECT s.id, s.name, s.smtp_host, s.status, s.health_score, s.daily_limit,
                COALESCE(sl_counts.sent_count, 0) as campaign_sent,
                COALESCE(sl_counts.bounce_count, 0) as campaign_bounced
            FROM servers s
            JOIN campaign_servers cs ON s.id = cs.server_id
            LEFT JOIN (
                SELECT server_id,
                    COUNT(*) as sent_count,
                    SUM(CASE WHEN status='bounced' OR status='failed' THEN 1 ELSE 0 END) as bounce_count
                FROM send_log WHERE campaign_id = ?
                GROUP BY server_id
            ) sl_counts ON s.id = sl_counts.server_id
            WHERE cs.campaign_id = ? AND s.deleted_at IS NULL
            ORDER BY cs.priority
        """, (campaign_id, campaign_id)).fetchall()

        # Get recent send log
        send_log = db.execute("""
            SELECT sl.*, c.email FROM send_log sl
            JOIN contacts c ON sl.contact_id = c.id
            WHERE sl.campaign_id = ?
            ORDER BY sl.sent_at DESC LIMIT 50
        """, (campaign_id,)).fetchall()

        # Get all active servers for test email
        all_servers = db.execute(
            "SELECT id, name, from_email FROM servers WHERE deleted_at IS NULL AND status IN ('active','warmup')"
        ).fetchall()

        # Count unsubscribed contacts for this campaign
        unsubscribed_count = db.execute("""
            SELECT COUNT(DISTINCT sl.contact_id) FROM send_log sl
            JOIN contacts c ON c.id = sl.contact_id
            WHERE sl.campaign_id = ? AND c.status = 'unsubscribed'
        """, (campaign_id,)).fetchone()[0]

    finally:
        db.close()

    return templates.TemplateResponse("campaigns/detail.html", {
        "request": request,
        "campaign": campaign,
        "template": tmpl,
        "contact_list": clist,
        "servers": servers,
        "send_log": send_log,
        "all_servers": all_servers,
        "unsubscribed_count": unsubscribed_count,
        "flash_message": flash,
        "flash_type": flash_type,
    })


@app.post("/campaigns/{campaign_id}/start")
def campaign_start(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaign = db.execute("SELECT status FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)).fetchone()
        if not campaign:
            return RedirectResponse("/campaigns", status_code=302)

        if campaign["status"] in ("draft", "paused", "scheduled"):
            db.execute("""
                UPDATE campaigns SET status='running', started_at=COALESCE(started_at, datetime('now')),
                    updated_at=datetime('now') WHERE id=?
            """, (campaign_id,))
            db.commit()

            # Trigger celery task
            try:
                from worker.tasks import run_campaign
                run_campaign.delay(campaign_id)
            except Exception as e:
                # Worker unavailable — revert status to draft
                db.execute("UPDATE campaigns SET status='draft', started_at=NULL WHERE id=?", (campaign_id,))
                db.commit()
                logger.error(f"Failed to dispatch campaign {campaign_id} to worker: {e}")
                return RedirectResponse(
                    f"/campaigns/{campaign_id}?flash=Nelze+spustit+kampaň,+worker+není+dostupný&flash_type=error",
                    status_code=302
                )

    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.post("/campaigns/{campaign_id}/pause")
def campaign_pause(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("""
            UPDATE campaigns SET status='paused', pause_reason='manual', updated_at=datetime('now')
            WHERE id=? AND status='running'
        """, (campaign_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.post("/campaigns/{campaign_id}/resume")
def campaign_resume(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaign = db.execute(
            "SELECT status FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)
        ).fetchone()

        if not campaign or campaign["status"] != "paused":
            # Not paused — may already be running, do not dispatch again
            return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)

        db.execute("""
            UPDATE campaigns SET status='running', pause_reason='', updated_at=datetime('now')
            WHERE id=? AND status='paused'
        """, (campaign_id,))
        db.commit()

        # Clear Redis batch state and lock so campaign starts fresh
        try:
            from worker.throttle import get_redis
            r = get_redis()
            r.delete(f"batch:campaign:{campaign_id}:pause_until")
            r.delete(f"batch:campaign:{campaign_id}:sent")
            r.delete(f"batch:campaign:{campaign_id}:server_idx")
            r.delete(f"batch:campaign:{campaign_id}:counter")
            r.delete(f"lock:campaign:{campaign_id}")
        except Exception:
            pass

        try:
            from worker.tasks import run_campaign
            run_campaign.delay(campaign_id)
        except Exception as e:
            db.execute("UPDATE campaigns SET status='paused' WHERE id=?", (campaign_id,))
            db.commit()
            logger.error(f"Failed to resume campaign {campaign_id}: {e}")
            return RedirectResponse(
                f"/campaigns/{campaign_id}?flash=Nelze+obnovit+kampaň,+worker+není+dostupný&flash_type=error",
                status_code=302
            )

    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.post("/campaigns/{campaign_id}/stop")
def campaign_stop(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("""
            UPDATE campaigns SET status='cancelled', completed_at=datetime('now'),
                updated_at=datetime('now')
            WHERE id=? AND status IN ('running', 'paused', 'scheduled')
        """, (campaign_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.get("/campaigns/{campaign_id}/edit", response_class=HTMLResponse)
def campaign_edit_form(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaign = db.execute("SELECT * FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)).fetchone()
        if not campaign or campaign["status"] not in ("draft", "paused", "cancelled", "completed"):
            return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)
        tmpls = db.execute("SELECT id, name FROM email_templates WHERE deleted_at IS NULL").fetchall()
        lists = db.execute("SELECT id, name FROM contact_lists WHERE deleted_at IS NULL").fetchall()
        servers = db.execute("SELECT id, name FROM servers WHERE deleted_at IS NULL AND status IN ('active','warmup')").fetchall()
        selected_server_ids = [r[0] for r in db.execute(
            "SELECT server_id FROM campaign_servers WHERE campaign_id=?", (campaign_id,)
        ).fetchall()]
    finally:
        db.close()
    return templates.TemplateResponse("campaigns/edit.html", {
        "request": request, "campaign": campaign,
        "templates_list": tmpls, "lists": lists, "servers": servers,
        "selected_server_ids": selected_server_ids,
    })


@app.post("/campaigns/{campaign_id}/edit")
async def campaign_update(request: Request, campaign_id: int):
    auth = require_auth(request)
    if auth:
        return auth

    f = await request.form()
    server_ids = f.get("server_ids", "")

    db = get_db()
    try:
        # Recount recipients
        list_id = int(f.get("list_id"))
        total = db.execute("""
            SELECT COUNT(DISTINCT c.id) FROM contacts c
            JOIN contact_list_members clm ON c.id = clm.contact_id
            WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
        """, (list_id,)).fetchone()[0]

        db.execute("""
            UPDATE campaigns SET name=?, template_id=?, list_id=?,
                throttle_total=?, throttle_window_minutes=?,
                throttle_interval_min=?, throttle_interval_max=?,
                server_rotation_mode=?, server_batch_size=?,
                total_recipients=?, updated_at=datetime('now')
            WHERE id=? AND deleted_at IS NULL
        """, (
            f.get("name"), int(f.get("template_id")), list_id,
            int(f.get("throttle_total", 100)), int(f.get("throttle_window_minutes", 30)),
            float(f.get("throttle_interval_min", 30)), float(f.get("throttle_interval_max", 42)),
            f.get("server_rotation_mode", "round_robin"), int(f.get("server_batch_size", 50)),
            total, campaign_id,
        ))

        # Update servers
        db.execute("DELETE FROM campaign_servers WHERE campaign_id=?", (campaign_id,))
        if server_ids:
            for i, sid in enumerate(server_ids.split(",")):
                if sid.strip():
                    db.execute(
                        "INSERT INTO campaign_servers (campaign_id, server_id, priority) VALUES (?, ?, ?)",
                        (campaign_id, int(sid.strip()), i)
                    )
        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.post("/campaigns/{campaign_id}/resend")
def campaign_resend(request: Request, campaign_id: int):
    """Reset a completed/cancelled campaign to draft so it can be re-sent."""
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        campaign = db.execute("SELECT status FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)).fetchone()
        if not campaign or campaign["status"] not in ("completed", "cancelled"):
            return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)

        # Reset campaign stats and status
        db.execute("""
            UPDATE campaigns SET status='draft',
                sent_count=0, delivered=0, opened=0, clicked=0,
                bounced=0, complained=0, failed=0,
                started_at=NULL, completed_at=NULL, updated_at=datetime('now')
            WHERE id=?
        """, (campaign_id,))

        # Delete tracking tokens first (FK references send_log)
        db.execute("""
            DELETE FROM email_tracking_tokens WHERE send_log_id IN (
                SELECT id FROM send_log WHERE campaign_id=?
            )
        """, (campaign_id,))

        # Delete old send log for this campaign
        db.execute("DELETE FROM send_log WHERE campaign_id=?", (campaign_id,))

        # Recount recipients (some may have bounced)
        list_id = db.execute("SELECT list_id FROM campaigns WHERE id=?", (campaign_id,)).fetchone()[0]
        total = db.execute("""
            SELECT COUNT(DISTINCT c.id) FROM contacts c
            JOIN contact_list_members clm ON c.id = clm.contact_id
            WHERE clm.list_id = ? AND c.status = 'active' AND c.deleted_at IS NULL
        """, (list_id,)).fetchone()[0]
        db.execute("UPDATE campaigns SET total_recipients=? WHERE id=?", (total, campaign_id))

        db.commit()
    finally:
        db.close()
    return RedirectResponse(f"/campaigns/{campaign_id}", status_code=302)


@app.post("/campaigns/{campaign_id}/test-email")
def campaign_test_email(
    request: Request,
    campaign_id: int,
    test_email: str = Form(...),
    test_server_id: int = Form(...),
):
    auth = require_auth(request)
    if auth:
        return auth

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from jinja2 import Template as J2Template

    db = get_db()
    result_msg = ""
    result_type = "success"
    try:
        campaign = db.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        tmpl = db.execute("SELECT * FROM email_templates WHERE id=?", (campaign["template_id"],)).fetchone()
        server = db.execute("SELECT * FROM servers WHERE id=?", (test_server_id,)).fetchone()

        if not all([campaign, tmpl, server]):
            result_msg = "Kampaň, šablona nebo server nenalezen."
            result_type = "error"
        else:
            # Render with test data
            test_data = {
                "first_name": "Test",
                "last_name": "Uživatel",
                "company": "Testovací Firma",
                "email": test_email,
                "unsubscribe_url": "#test-unsubscribe",
            }
            subject = J2Template(tmpl["subject"]).render(**test_data)
            html_body = J2Template(tmpl["html_body"]).render(**test_data)
            text_body = J2Template(tmpl["text_body"] or "").render(**test_data)

            subject = f"[TEST] {subject}"

            # Send
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{server['from_name']} <{server['from_email']}>" if server["from_name"] else server["from_email"]
            msg["To"] = test_email
            msg["Subject"] = subject
            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            try:
                if server["use_tls"]:
                    smtp = smtplib.SMTP(server["smtp_host"], server["smtp_port"], timeout=15)
                    smtp.starttls()
                else:
                    smtp = smtplib.SMTP(server["smtp_host"], server["smtp_port"], timeout=15)
                smtp.login(server["smtp_user"], server["smtp_password"])
                # Use smtp_user as envelope sender (Mailcow requires this)
                envelope_from = server["smtp_user"]
                smtp.sendmail(envelope_from, [test_email], msg.as_string())
                smtp.quit()
                result_msg = f"Testovací email odeslán na {test_email} přes {server['name']}."
            except Exception as e:
                result_msg = f"Chyba odesílání: {str(e)}"
                result_type = "error"
    finally:
        db.close()

    # Redirect back with flash message (simple query param approach)
    return RedirectResponse(
        f"/campaigns/{campaign_id}?flash={result_msg}&flash_type={result_type}",
        status_code=302
    )


# ══════════════════════════════════════════════════════════
# SERVER SMTP TEST
# ══════════════════════════════════════════════════════════

def _server_flash(key: str, **subs) -> str:
    """
    Build a flash message in the active request language.
    Translates the key, then substitutes placeholders:
      %s -> server name, %h -> host, %p -> port,
      %e -> recipient email, %n -> count
    """
    from app.core.translations import t as _t
    msg = _t(key, _current_lang.get())
    for placeholder, value in subs.items():
        msg = msg.replace(placeholder, str(value))
    return msg


@app.post("/servers/{server_id}/test")
def server_test_smtp(request: Request, server_id: int):
    auth = require_auth(request)
    if auth:
        return auth

    import smtplib
    import socket
    import ssl as ssl_module

    db = get_db()
    try:
        server = db.execute("SELECT * FROM servers WHERE id=? AND deleted_at IS NULL", (server_id,)).fetchone()
        if not server:
            return RedirectResponse("/servers", status_code=302)

        flash = ""
        flash_type = "success"
        log_detail = ""

        sname = server["name"]
        shost = server["smtp_host"]
        sport = server["smtp_port"]

        try:
            if server["use_tls"]:
                smtp = smtplib.SMTP(shost, sport, timeout=15)
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(shost, sport, timeout=15)
            smtp.login(server["smtp_user"], server["smtp_password"])
            smtp.quit()

            flash = _server_flash("stest_smtp_ok", **{"%s": sname})
            flash_type = "success"
            log_detail = "Manual SMTP test successful"

            # Update health on success
            db.execute("""
                UPDATE servers SET health_score = 100, last_health_check = datetime('now')
                WHERE id = ?
            """, (server_id,))
            db.execute("""
                INSERT INTO server_health_log (server_id, event_type, detail)
                VALUES (?, 'test_ok', ?)
            """, (server_id, log_detail))
            db.commit()

        except smtplib.SMTPAuthenticationError as e:
            flash = _server_flash("stest_auth_error", **{"%s": sname})
            flash_type = "error"
            log_detail = f"Auth error: {str(e)[:200]}"

        except smtplib.SMTPConnectError as e:
            flash = _server_flash("stest_connect_error", **{"%s": sname, "%h": shost, "%p": sport})
            flash_type = "error"
            log_detail = f"Connect error: {str(e)[:200]}"

        except smtplib.SMTPServerDisconnected as e:
            flash = _server_flash("stest_disconnected", **{"%s": sname})
            flash_type = "error"
            log_detail = f"Disconnect: {str(e)[:200]}"

        except (socket.gaierror, socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
            # Network-level: DNS failed, timeout, connection refused, host unreachable, etc.
            flash = _server_flash("stest_unreachable", **{"%s": sname, "%h": shost, "%p": sport})
            flash_type = "error"
            log_detail = f"Network error: {type(e).__name__}: {str(e)[:200]}"

        except ssl_module.SSLError as e:
            flash = _server_flash("stest_ssl_error", **{"%s": sname})
            flash_type = "error"
            log_detail = f"SSL error: {str(e)[:200]}"

        except Exception as e:
            # Catch-all — show generic localized message; keep technical detail in log
            flash = _server_flash("stest_other_error", **{"%s": sname}) + f" – {type(e).__name__}"
            flash_type = "error"
            log_detail = f"Other error: {type(e).__name__}: {str(e)[:200]}"

        # Log failure (only if there was a failure — success path already logged above)
        if flash_type == "error":
            try:
                db.execute("""
                    INSERT INTO server_health_log (server_id, event_type, detail)
                    VALUES (?, 'test_fail', ?)
                """, (server_id, log_detail))
                db.commit()
            except Exception:
                pass  # Don't let logging failure mask the test result

    finally:
        db.close()

    # URL-encode flash so special chars (&, spaces, UTF-8) don't break the redirect
    return RedirectResponse(
        f"/servers?flash={quote(flash)}&flash_type={flash_type}",
        status_code=302,
    )


@app.post("/servers/{server_id}/test-email")
def server_test_send_email(
    request: Request,
    server_id: int,
    test_email: str = Form(...),
):
    auth = require_auth(request)
    if auth:
        return auth

    import smtplib
    import socket
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    db = get_db()
    try:
        server = db.execute("SELECT * FROM servers WHERE id=? AND deleted_at IS NULL", (server_id,)).fetchone()
        if not server:
            return RedirectResponse("/servers", status_code=302)

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{server['from_name']} <{server['from_email']}>" if server["from_name"] else server["from_email"]
        msg["To"] = test_email
        msg["Subject"] = f"[TEST] CampaignPilot – test serveru {server['name']}"
        msg.attach(MIMEText(
            f"Tento email potvrzuje, že server {server['name']} ({server['smtp_host']}) odesílá správně.\n\n"
            f"Odesláno: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"From: {server['from_email']}\n"
            f"Server: {server['smtp_host']}:{server['smtp_port']}",
            "plain", "utf-8"
        ))
        msg.attach(MIMEText(
            f"""<html><body style="font-family:sans-serif;padding:20px;">
            <h2 style="color:#06d6a0;">✓ SMTP Test úspěšný</h2>
            <p>Server <strong>{server['name']}</strong> ({server['smtp_host']}) odesílá správně.</p>
            <table style="margin-top:16px;border-collapse:collapse;">
            <tr><td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold;">Server</td><td style="padding:6px 12px;border:1px solid #ddd;">{server['name']}</td></tr>
            <tr><td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold;">SMTP</td><td style="padding:6px 12px;border:1px solid #ddd;">{server['smtp_host']}:{server['smtp_port']}</td></tr>
            <tr><td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold;">From</td><td style="padding:6px 12px;border:1px solid #ddd;">{server['from_email']}</td></tr>
            <tr><td style="padding:6px 12px;border:1px solid #ddd;font-weight:bold;">Čas</td><td style="padding:6px 12px;border:1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            </table>
            </body></html>""",
            "html", "utf-8"
        ))

        try:
            if server["use_tls"]:
                smtp_conn = smtplib.SMTP(server["smtp_host"], server["smtp_port"], timeout=15)
                smtp_conn.starttls()
            else:
                smtp_conn = smtplib.SMTP(server["smtp_host"], server["smtp_port"], timeout=15)
            smtp_conn.login(server["smtp_user"], server["smtp_password"])
            smtp_conn.sendmail(server["smtp_user"], [test_email], msg.as_string())
            smtp_conn.quit()
            flash = _server_flash("stest_email_sent", **{"%e": test_email, "%s": server["name"]})
            flash_type = "success"
        except smtplib.SMTPAuthenticationError:
            flash = _server_flash("stest_auth_error", **{"%s": server["name"]})
            flash_type = "error"
        except smtplib.SMTPRecipientsRefused:
            flash = _server_flash("stest_email_recipient_refused", **{"%s": server["name"], "%e": test_email})
            flash_type = "error"
        except (socket.gaierror, socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
            flash = _server_flash("stest_unreachable", **{
                "%s": server["name"], "%h": server["smtp_host"], "%p": server["smtp_port"]
            }) + f" – {type(e).__name__}"
            flash_type = "error"
        except Exception as e:
            flash = _server_flash("stest_email_send_error") + f": {type(e).__name__} – {str(e)[:80]}"
            flash_type = "error"

    finally:
        db.close()

    return RedirectResponse(
        f"/servers?flash={quote(flash)}&flash_type={flash_type}",
        status_code=302,
    )


@app.post("/servers/{server_id}/test-imap")
def server_test_imap(request: Request, server_id: int):
    auth = require_auth(request)
    if auth:
        return auth

    import imaplib
    import socket
    import ssl as ssl_module

    db = get_db()
    try:
        server = db.execute("SELECT * FROM servers WHERE id=? AND deleted_at IS NULL", (server_id,)).fetchone()
        if not server:
            return RedirectResponse("/servers", status_code=302)
        if not server["bounce_check_enabled"]:
            return RedirectResponse(
                f"/servers?flash={quote(_server_flash('stest_imap_disabled'))}&flash_type=error",
                status_code=302,
            )

        flash = ""
        flash_type = "success"

        ihost = server["bounce_imap_host"]
        iport = server["bounce_imap_port"]

        try:
            if server["bounce_imap_ssl"]:
                imap = imaplib.IMAP4_SSL(ihost, iport, timeout=15)
            else:
                imap = imaplib.IMAP4(ihost, iport, timeout=15)

            imap.login(server["bounce_imap_user"], server["bounce_imap_password"])
            imap.list()
            status, messages = imap.select("INBOX")
            msg_count = int(messages[0]) if messages and messages[0] else 0
            imap.close()
            imap.logout()

            flash = _server_flash("stest_imap_ok", **{"%h": ihost, "%n": msg_count})
            flash_type = "success"

        except imaplib.IMAP4.error as e:
            # Login failed, mailbox doesn't exist, etc. Show technical reason as suffix.
            flash = _server_flash("stest_imap_error") + f": {str(e)[:120]}"
            flash_type = "error"

        except (socket.gaierror, socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
            flash = _server_flash("stest_imap_unreachable", **{"%h": ihost, "%p": iport}) + f" – {type(e).__name__}"
            flash_type = "error"

        except ssl_module.SSLError as e:
            flash = _server_flash("stest_imap_ssl_error") + f": {str(e)[:120]}"
            flash_type = "error"

        except Exception as e:
            flash = _server_flash("stest_imap_error") + f": {type(e).__name__} – {str(e)[:80]}"
            flash_type = "error"

    finally:
        db.close()

    return RedirectResponse(
        f"/servers?flash={quote(flash)}&flash_type={flash_type}",
        status_code=302,
    )


# ══════════════════════════════════════════════════════════
# DOMAIN LIMITS
# ══════════════════════════════════════════════════════════

@app.post("/domains/{domain_id}/block")
def domain_block(request: Request, domain_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute(
            "UPDATE destination_limits SET blocked=1, block_reason='Manuální blokace' WHERE id=?",
            (domain_id,)
        )
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/domains", status_code=302)


@app.post("/domains/{domain_id}/unblock")
def domain_unblock(request: Request, domain_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        # Get domain name
        domain_row = db.execute("SELECT domain FROM destination_limits WHERE id=?", (domain_id,)).fetchone()
        db.execute("UPDATE destination_limits SET blocked=0, block_reason='' WHERE id=?", (domain_id,))
        if domain_row:
            domain = domain_row["domain"]
            # Remove blocked send_log records only for RUNNING campaigns
            # so contacts get sent in current run
            db.execute("""
                DELETE FROM send_log WHERE status='blocked'
                AND campaign_id IN (SELECT id FROM campaigns WHERE status='running')
                AND contact_id IN (
                    SELECT id FROM contacts WHERE email LIKE ?
                )
            """, (f"%@{domain}",))
            # Recalculate blocked_count only for running campaigns
            db.execute("""
                UPDATE campaigns SET blocked_count = (
                    SELECT COUNT(*) FROM send_log WHERE campaign_id=campaigns.id AND status='blocked'
                ) WHERE status='running'
            """)
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/domains", status_code=302)


@app.get("/domains", response_class=HTMLResponse)
def domains_list(request: Request):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        domains = db.execute("SELECT * FROM destination_limits ORDER BY domain").fetchall()
    finally:
        db.close()

    # Enrich with live Redis counters
    from worker.throttle import get_redis
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        r = get_redis()
        now = datetime.now(ZoneInfo("Europe/Prague"))
        hour_str = now.strftime("%Y%m%d%H")
        day_str = now.strftime("%Y%m%d")
        domains_enriched = []
        for d in domains:
            d = dict(d)
            domain = d["domain"]
            hour_val = r.get(f"throttle:domain:{domain}:hour:{hour_str}")
            day_val = r.get(f"throttle:domain:{domain}:day:{day_str}")
            d["sent_this_hour"] = int(hour_val) if hour_val else 0
            d["sent_today"] = int(day_val) if day_val else 0
            block_val = r.get(f"block:domain:{domain}")
            d["reputation_block"] = block_val.decode() if block_val else None
            domains_enriched.append(d)
    except Exception:
        domains_enriched = [dict(d) for d in domains]

    return templates.TemplateResponse("domains/list.html", {"request": request, "domains": domains_enriched})


@app.post("/domains/new")
def domain_create(
    request: Request,
    domain: str = Form(...),
    max_per_hour: int = Form(100),
    max_per_day: int = Form(1000),
):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute(
            "INSERT OR REPLACE INTO destination_limits (domain, max_per_hour, max_per_day) VALUES (?, ?, ?)",
            (domain.strip().lower(), max_per_hour, max_per_day)
        )
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/domains", status_code=302)


@app.post("/domains/{domain_id}/delete")
def domain_delete(request: Request, domain_id: int):
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("DELETE FROM destination_limits WHERE id=?", (domain_id,))
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/domains", status_code=302)


# ══════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=WEB_HOST, port=WEB_PORT, reload=True)




@app.get("/campaigns/{campaign_id}/report")
def campaign_report(request: Request, campaign_id: int):
    """Generate and download a Markdown report for a campaign."""
    auth = require_auth(request)
    if auth:
        return auth

    db = get_db()
    try:
        campaign = db.execute(
            "SELECT * FROM campaigns WHERE id=? AND deleted_at IS NULL", (campaign_id,)
        ).fetchone()
        if not campaign:
            return RedirectResponse("/campaigns", status_code=302)
        campaign = dict(campaign)

    finally:
        db.close()

    # Calculate duration
    duration_str = "–"
    if campaign.get("started_at") and campaign.get("completed_at"):
        from datetime import datetime
        try:
            started = datetime.fromisoformat(campaign["started_at"])
            completed = datetime.fromisoformat(campaign["completed_at"])
            delta = completed - started
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                duration_str = f"{hours}h {minutes}min"
            else:
                duration_str = f"{minutes}min {seconds}s"
        except Exception:
            pass

    # Calculate percentages
    delivered = campaign.get("delivered", 0) or 0
    sent = campaign.get("sent_count", 0) or 0
    bounced = campaign.get("bounced", 0) or 0
    opened = campaign.get("opened", 0) or 0
    clicked = campaign.get("clicked", 0) or 0
    failed = campaign.get("failed", 0) or 0

    open_rate = f"{opened / delivered * 100:.1f}%" if delivered > 0 else "–"
    click_rate = f"{clicked / delivered * 100:.1f}%" if delivered > 0 else "–"
    bounce_rate = f"{bounced / sent * 100:.1f}%" if sent > 0 else "–"
    delivery_rate = f"{delivered / sent * 100:.1f}%" if sent > 0 else "–"

    started_str = campaign.get("started_at", "–") or "–"
    completed_str = campaign.get("completed_at", "–") or "–"

    # Build Markdown - clean aligned format
    def row(label, value, pct=""):
        pct_str = f"  ({pct})" if pct and pct != "–" else ""
        return f"{label:<16} {value}{pct_str}"

    lines = [
        f"# Statistika kampaně: {campaign['name']}",
        "",
        row("Stav:", campaign["status"]),
        row("Zahájeno:", started_str[:16] if started_str != "–" else "–"),
        row("Dokončeno:", completed_str[:16] if completed_str != "–" else "–"),
        row("Trvání:", duration_str),
        "",
        row("Odesláno:", sent),
        row("Doručeno:", delivered, delivery_rate),
        row("Bounced:", bounced, bounce_rate),
        row("Otevřeno:", opened, open_rate),
        row("Kliknuto:", clicked, click_rate),
        row("Selhalo:", failed),
    ]

    lines += [
        "",
        "---",
        f"Vygenerováno: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]

    report = "\n".join(lines)
    filename = f"kampan_{campaign_id}_{campaign['name'].replace(' ', '_')[:30]}.md"

    return Response(
        content=report,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )


# ══════════════════════════════════════════════════════════
# UNSUBSCRIBE
# ══════════════════════════════════════════════════════════

@app.get("/unsubscribe/{token}/{contact_id}/{campaign_id}", response_class=HTMLResponse)
def unsubscribe(request: Request, token: str, contact_id: int, campaign_id: int):
    """Handle unsubscribe link from email. Token is HMAC-SHA256 signed."""
    from app.config import SECRET_KEY

    # Verify HMAC token
    expected = hmac.new(
        SECRET_KEY.encode(),
        f"{contact_id}:{campaign_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(token, expected):
        return HTMLResponse("<html><body><h2>Odkaz není platný nebo vypršel.</h2></body></html>", status_code=400)

    db = get_db()
    try:
        contact = db.execute(
            "SELECT email, status FROM contacts WHERE id=? AND deleted_at IS NULL", (contact_id,)
        ).fetchone()

        if not contact:
            return HTMLResponse("<html><body><h2>Kontakt nebyl nalezen.</h2></body></html>", status_code=404)

        if contact["status"] != "unsubscribed":
            db.execute(
                "UPDATE contacts SET status='unsubscribed', updated_at=datetime('now') WHERE id=?",
                (contact_id,)
            )
            db.commit()

        email = contact["email"]
    finally:
        db.close()

    return HTMLResponse(f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Odhlášení z odběru</title>
        <style>
            body {{ font-family: sans-serif; display: flex; justify-content: center;
                   align-items: center; min-height: 100vh; margin: 0;
                   background: #f5f5f5; color: #333; }}
            .box {{ background: white; padding: 40px; border-radius: 8px;
                   text-align: center; max-width: 480px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
            h2 {{ margin-top: 0; color: #222; }}
            p {{ color: #666; line-height: 1.6; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Byli jste odhlášeni</h2>
            <p>Adresa <strong>{email}</strong> byla úspěšně odhlášena z odběru.</p>
            <p>Již vám nebudeme zasílat žádná sdělení.</p>
        </div>
    </body>
    </html>
    """)

# ══════════════════════════════════════════════════════════
# RESET CONTACT STATISTICS
# ══════════════════════════════════════════════════════════

@app.post("/contacts/reset-stats")
def contacts_reset_stats(request: Request):
    """Reset open and click tracking for all contacts."""
    auth = require_auth(request)
    if auth:
        return auth
    db = get_db()
    try:
        db.execute("UPDATE send_log SET opened_at=NULL, clicked_at=NULL")
        db.execute("UPDATE campaigns SET opened=0, clicked=0")
        db.commit()
    finally:
        db.close()
    return RedirectResponse("/contacts?flash=Statistiky+otevření+a+kliknutí+byly+resetovány&flash_type=success", status_code=302)

# ══════════════════════════════════════════════════════════
# GEO IP LOOKUP
# ══════════════════════════════════════════════════════════

def _get_client_ip(request: Request) -> str:
    """Get real client IP from X-Forwarded-For or direct connection."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""


def _geo_lookup(ip: str) -> tuple:
    """Return (country_code, country_name) for given IP. Returns ('', '') on failure."""
    if not ip or ip in ("127.0.0.1", "::1", "localhost"):
        return ("", "")
    try:
        with geoip2.database.Reader(GEOIP_PATH) as reader:
            response = reader.country(ip)
            code = response.country.iso_code or ""
            name = response.country.name or ""
            return (code, name)
    except Exception:
        return ("", "")


# Confidence scores per source
_GEO_CONFIDENCE = {"open": 0.6, "click": 1.0}


def _update_contact_geo(db, contact_id: int, ip: str, source: str):
    """
    Update contact geo data using confidence model.
    Rule: update only if new_confidence > existing_confidence
    This ensures click data never gets overwritten by open (proxy) data.
    """
    new_confidence = _GEO_CONFIDENCE.get(source, 0)
    if new_confidence == 0:
        return

    existing = db.execute(
        "SELECT geo_confidence FROM contacts WHERE id=?", (contact_id,)
    ).fetchone()

    if not existing:
        return

    existing_confidence = existing["geo_confidence"] or 0

    # Only update if new source has strictly higher confidence
    if new_confidence <= existing_confidence:
        return

    country_code, country_name = _geo_lookup(ip)
    if not country_code:
        return

    db.execute("""
        UPDATE contacts SET
            geo_country_code=?, geo_country_name=?,
            geo_source=?, geo_confidence=?,
            geo_ip=?, geo_updated_at=datetime('now')
        WHERE id=?
    """, (country_code, country_name, source, new_confidence, ip, contact_id))


# ══════════════════════════════════════════════════════════
# EMAIL TRACKING (no auth required - called by email clients)
# ══════════════════════════════════════════════════════════

# 1x1 transparent GIF
_TRACKING_PIXEL = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'


@app.get("/track/open/{token}")
def track_open(token: str, request: Request):
    """Record email open via invisible tracking pixel. Also captures geo data."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM email_tracking_tokens WHERE token=?", (token,)
        ).fetchone()
        if row:
            # Skip tracking for bounced contacts
            contact_status = db.execute(
                "SELECT status FROM contacts WHERE id=?", (row["contact_id"],)
            ).fetchone()
            if contact_status and contact_status["status"] in ("bounced", "unsubscribed"):
                pass
            else:
                existing = db.execute(
                    "SELECT opened_at FROM send_log WHERE id=?", (row["send_log_id"],)
                ).fetchone()
                if existing and not existing["opened_at"]:
                    db.execute(
                        "UPDATE send_log SET opened_at=datetime('now'), status='opened' WHERE id=?",
                        (row["send_log_id"],)
                    )
                    db.execute(
                        "UPDATE campaigns SET opened=opened+1 WHERE id=?",
                        (row["campaign_id"],)
                    )
                    db.commit()  # commit tracking first, geo is best-effort
                # Geo lookup — zdroj: open (confidence=0.6)
                try:
                    ip = _get_client_ip(request)
                    if ip:
                        _update_contact_geo(db, row["contact_id"], ip, "open")
                        db.commit()
                except Exception:
                    pass
    except Exception:
        pass
    finally:
        db.close()
    return Response(
        content=_TRACKING_PIXEL,
        media_type="image/gif",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"},
    )


@app.get("/track/click/{token}")
def track_click(token: str, request: Request, url: str = ""):
    """Record link click and redirect to original URL. Also captures geo data."""
    db = get_db()
    try:
        row = db.execute(
            "SELECT * FROM email_tracking_tokens WHERE token=?", (token,)
        ).fetchone()
        if row:
            # Skip tracking for bounced contacts
            contact_status = db.execute(
                "SELECT status FROM contacts WHERE id=?", (row["contact_id"],)
            ).fetchone()
            if contact_status and contact_status["status"] in ("bounced", "unsubscribed"):
                pass
            else:
                existing = db.execute(
                    "SELECT clicked_at FROM send_log WHERE id=?", (row["send_log_id"],)
                ).fetchone()
                if existing and not existing["clicked_at"]:
                    db.execute(
                        "UPDATE send_log SET clicked_at=datetime('now'), status='clicked' WHERE id=?",
                        (row["send_log_id"],)
                    )
                    db.execute(
                        "UPDATE campaigns SET clicked=clicked+1 WHERE id=?",
                        (row["campaign_id"],)
                    )
                    db.commit()  # commit tracking first, geo is best-effort
                # Geo lookup — zdroj: click (confidence=1.0)
                try:
                    ip = _get_client_ip(request)
                    if ip:
                        _update_contact_geo(db, row["contact_id"], ip, "click")
                        db.commit()
                except Exception:
                    pass
    except Exception:
        pass
    finally:
        db.close()
    destination = unquote(url) if url else "/"
    return RedirectResponse(destination, status_code=302)