import sqlite3
import os
from app.config import DB_PATH


def get_db() -> sqlite3.Connection:
    """Get database connection with WAL mode and row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    # Ensure we always see the latest committed data from other connections
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    """Initialize database schema."""
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # ── Servers (mail server pool) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            smtp_host TEXT NOT NULL,
            smtp_port INTEGER DEFAULT 587,
            smtp_user TEXT NOT NULL,
            smtp_password TEXT NOT NULL,
            use_tls INTEGER DEFAULT 1,
            from_email TEXT NOT NULL,
            from_name TEXT DEFAULT '',
            daily_limit INTEGER DEFAULT 500,
            hourly_limit INTEGER DEFAULT 100,
            sent_today INTEGER DEFAULT 0,
            sent_this_hour INTEGER DEFAULT 0,
            weight INTEGER DEFAULT 50,
            status TEXT DEFAULT 'active' CHECK(status IN ('active','paused','warmup','blacklisted')),
            warmup_day INTEGER DEFAULT 0,
            health_score INTEGER DEFAULT 100,
            last_health_check TEXT,
            last_hour_reset TEXT,
            last_day_reset TEXT,
            bounce_check_enabled INTEGER DEFAULT 0,
            bounce_imap_host TEXT DEFAULT '',
            bounce_imap_port INTEGER DEFAULT 993,
            bounce_imap_user TEXT DEFAULT '',
            bounce_imap_password TEXT DEFAULT '',
            bounce_imap_ssl INTEGER DEFAULT 1,
            bounce_last_check TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT
        )
    """)

    # ── Contact Lists ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            contact_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT
        )
    """)

    # ── Contacts ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT DEFAULT '',
            last_name TEXT DEFAULT '',
            company TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            status TEXT DEFAULT 'active' CHECK(status IN ('active','unsubscribed','bounced','invalid','cleaned')),
            bounce_count INTEGER DEFAULT 0,
            last_bounce_at TEXT,
            bounce_type TEXT,
            source TEXT DEFAULT 'manual',
            mx_valid INTEGER DEFAULT 0,
            validated_at TEXT,
            custom_fields TEXT DEFAULT '{}',
            geo_country_code TEXT DEFAULT '',
            geo_country_name TEXT DEFAULT '',
            geo_source TEXT DEFAULT '',
            geo_confidence REAL DEFAULT 0,
            geo_ip TEXT DEFAULT '',
            geo_updated_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT
        )
    """)

    # ── Contact <-> List (M:N) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_list_members (
            contact_id INTEGER NOT NULL,
            list_id INTEGER NOT NULL,
            added_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (contact_id, list_id),
            FOREIGN KEY (contact_id) REFERENCES contacts(id),
            FOREIGN KEY (list_id) REFERENCES contact_lists(id)
        )
    """)

    # ── Layouts (email skeletons) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS layouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            html_body TEXT NOT NULL DEFAULT '<html><body>{{content}}</body></html>',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT
        )
    """)

    # ── Email Templates ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            layout_id INTEGER,
            subject TEXT NOT NULL DEFAULT '',
            content_json TEXT DEFAULT '[]',
            html_body TEXT DEFAULT '',
            text_body TEXT DEFAULT '',
            variables TEXT DEFAULT '[]',
            spam_score INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT,
            FOREIGN KEY (layout_id) REFERENCES layouts(id)
        )
    """)

    # ── Template Versions ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS template_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            version_number INTEGER NOT NULL,
            subject TEXT,
            html_body TEXT,
            text_body TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (template_id) REFERENCES email_templates(id)
        )
    """)

    # ── Campaigns ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            template_id INTEGER,
            list_id INTEGER,
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft','scheduled','running','paused','completed','cancelled')),
            scheduled_at TEXT,
            throttle_total INTEGER DEFAULT 100,
            throttle_window_minutes INTEGER DEFAULT 60,
            throttle_interval_min REAL DEFAULT 3.0,
            throttle_interval_max REAL DEFAULT 7.0,
            server_rotation_mode TEXT DEFAULT 'round_robin' CHECK(server_rotation_mode IN ('round_robin','batch','weighted')),
            server_batch_size INTEGER DEFAULT 50,
            total_recipients INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            delivered INTEGER DEFAULT 0,
            opened INTEGER DEFAULT 0,
            clicked INTEGER DEFAULT 0,
            bounced INTEGER DEFAULT 0,
            complained INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            target_country TEXT DEFAULT '',
            pause_reason TEXT DEFAULT '',
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            deleted_at TEXT,
            FOREIGN KEY (template_id) REFERENCES email_templates(id),
            FOREIGN KEY (list_id) REFERENCES contact_lists(id)
        )
    """)

    # ── Campaign <-> Server mapping ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_servers (
            campaign_id INTEGER NOT NULL,
            server_id INTEGER NOT NULL,
            priority INTEGER DEFAULT 0,
            PRIMARY KEY (campaign_id, server_id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (server_id) REFERENCES servers(id)
        )
    """)

    # ── Send Log ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS send_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            contact_id INTEGER NOT NULL,
            server_id INTEGER,
            status TEXT DEFAULT 'queued' CHECK(status IN ('queued','sending','delivered','bounced','failed','opened','clicked','blocked')),
            message_id TEXT,
            sent_at TEXT,
            delivered_at TEXT,
            opened_at TEXT,
            clicked_at TEXT,
            bounce_type TEXT,
            error_message TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (contact_id) REFERENCES contacts(id),
            FOREIGN KEY (server_id) REFERENCES servers(id),
            UNIQUE(campaign_id, contact_id)
        )
    """)

    # ── Destination Rate Limits ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS destination_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL UNIQUE,
            max_per_hour INTEGER DEFAULT 100,
            max_per_day INTEGER DEFAULT 1000,
            sent_this_hour INTEGER DEFAULT 0,
            sent_today INTEGER DEFAULT 0,
            preferred_server_id INTEGER,
            last_hour_reset TEXT,
            last_day_reset TEXT,
            blocked INTEGER DEFAULT 0,
            block_reason TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (preferred_server_id) REFERENCES servers(id)
        )
    """)


    # ── Email Tracking Tokens ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_tracking_tokens (
            token TEXT PRIMARY KEY,
            send_log_id INTEGER NOT NULL,
            campaign_id INTEGER NOT NULL,
            contact_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (send_log_id) REFERENCES send_log(id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_token ON email_tracking_tokens(token)")

    # ── Webhook Events ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message_id TEXT,
            payload TEXT DEFAULT '{}',
            processed INTEGER DEFAULT 0,
            received_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Server Health Log ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_health_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            detail TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (server_id) REFERENCES servers(id)
        )
    """)

    # ── Indexes ──
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_send_log_campaign ON send_log(campaign_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_send_log_contact ON send_log(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_send_log_status ON send_log(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_send_log_msg_id ON send_log(message_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_destination_domain ON destination_limits(domain)")

    # ── App settings (single-row key-value store for admin credentials & prefs) ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Insert default destination limits ──
    cursor.execute("""
        INSERT OR IGNORE INTO destination_limits (domain, max_per_hour, max_per_day) VALUES
        ('gmail.com', 150, 2000),
        ('seznam.cz', 50, 500),
        ('email.cz', 50, 500),
        ('centrum.cz', 50, 500),
        ('outlook.com', 100, 1500),
        ('hotmail.com', 100, 1500),
        ('yahoo.com', 80, 1000)
    """)

    # ── Migrations for existing databases ──
    # ── Migrations — add missing columns to existing databases ──
    # Safe: ALTER TABLE ADD COLUMN is idempotent (silently skips if column exists)
    migrate_columns = [
        # Servers
        ("servers", "bounce_check_enabled", "INTEGER DEFAULT 0"),
        ("servers", "bounce_imap_host", "TEXT DEFAULT ''"),
        ("servers", "bounce_imap_port", "INTEGER DEFAULT 993"),
        ("servers", "bounce_imap_user", "TEXT DEFAULT ''"),
        ("servers", "bounce_imap_password", "TEXT DEFAULT ''"),
        ("servers", "bounce_imap_ssl", "INTEGER DEFAULT 1"),
        ("servers", "bounce_last_check", "TEXT"),
        ("servers", "bounce_last_uid", "INTEGER DEFAULT 0"),
        # Contacts — geo data
        ("contacts", "geo_country_code", "TEXT DEFAULT ''"),
        ("contacts", "geo_country_name", "TEXT DEFAULT ''"),
        ("contacts", "geo_source", "TEXT DEFAULT ''"),
        ("contacts", "geo_confidence", "REAL DEFAULT 0"),
        ("contacts", "geo_ip", "TEXT DEFAULT ''"),
        ("contacts", "geo_updated_at", "TEXT"),
        # Campaigns
        ("campaigns", "target_country", "TEXT DEFAULT ''"),
        ("campaigns", "pause_reason", "TEXT DEFAULT ''"),
        ("campaigns", "blocked_count", "INTEGER DEFAULT 0"),
        # Destination limits — domain blocking
        ("destination_limits", "blocked", "INTEGER DEFAULT 0"),
        ("destination_limits", "block_reason", "TEXT DEFAULT ''"),
        # Email templates — preheader
        ("email_templates", "preheader", "TEXT DEFAULT ''"),
        # Servers — per-server tracking domain
        ("servers", "tracking_domain", "TEXT DEFAULT ''"),
    ]
    for table, col, col_type in migrate_columns:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # Column already exists — safe to ignore

    # ── Migration: send_log CHECK constraint — add 'blocked' status ──
    # SQLite nemůže ALTER TABLE měnit CHECK constraint — musíme recreate tabulku
    # Detekujeme starý constraint bez 'blocked' a provedeme migraci
    send_log_sql = cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='send_log'"
    ).fetchone()
    if send_log_sql and "'blocked'" not in send_log_sql[0]:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.commit()
        # Cleanup any leftovers from previous failed migration attempts
        cursor.execute("DROP TABLE IF EXISTS send_log_migrated")
        cursor.execute("DROP TABLE IF EXISTS email_tracking_tokens_backup")
        # Backup email_tracking_tokens (FK depends on send_log)
        cursor.execute("ALTER TABLE email_tracking_tokens RENAME TO email_tracking_tokens_backup")
        cursor.execute("""
            CREATE TABLE send_log_migrated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                contact_id INTEGER NOT NULL,
                server_id INTEGER,
                status TEXT DEFAULT 'queued' CHECK(status IN ('queued','sending','delivered','bounced','failed','opened','clicked','blocked')),
                message_id TEXT,
                sent_at TEXT,
                delivered_at TEXT,
                opened_at TEXT,
                clicked_at TEXT,
                bounce_type TEXT,
                error_message TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id),
                FOREIGN KEY (server_id) REFERENCES servers(id),
                UNIQUE(campaign_id, contact_id)
            )
        """)
        cursor.execute("INSERT INTO send_log_migrated SELECT * FROM send_log")
        cursor.execute("DROP TABLE send_log")
        cursor.execute("ALTER TABLE send_log_migrated RENAME TO send_log")
        cursor.execute("ALTER TABLE email_tracking_tokens_backup RENAME TO email_tracking_tokens")
        conn.commit()
        conn.execute("PRAGMA foreign_keys=ON")
        print("Migration: send_log CHECK constraint updated to include 'blocked'")

    # ── Health check — verify all critical columns exist ──
    health_checks = {
        "contacts": ["geo_country_code", "geo_country_name", "geo_source",
                     "geo_confidence", "geo_ip", "geo_updated_at"],
        "campaigns": ["target_country"],
        "servers": ["bounce_check_enabled", "bounce_imap_host"],
    }
    for table, cols in health_checks.items():
        existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})")}
        missing = [c for c in cols if c not in existing]
        if missing:
            print(f"WARNING: {table} missing columns: {missing}")
        else:
            print(f"OK: {table} schema valid")

    # Performance indexes
    indexes = [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_send_log_unique ON send_log(campaign_id, contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_send_log_campaign_contact ON send_log(campaign_id, contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_send_log_contact ON send_log(contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_contacts_status_deleted ON contacts(status, deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_clm_list_contact ON contact_list_members(list_id, contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_tracking_token ON email_tracking_tokens(token)",
        "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status, deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)",
        "CREATE INDEX IF NOT EXISTS idx_send_log_status ON send_log(campaign_id, status)",
    ]
    for idx in indexes:
        try:
            cursor.execute(idx)
        except Exception:
            pass

    conn.commit()
    conn.close()
    print("Database initialized successfully.")