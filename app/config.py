import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "CampaignPilot")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

DB_PATH = os.getenv("DB_PATH", "./data/campaign_manager.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

POSTAL_API_URL = os.getenv("POSTAL_API_URL", "")
POSTAL_API_KEY = os.getenv("POSTAL_API_KEY", "")

WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", 8080))
APP_BASE_URL = os.getenv("APP_BASE_URL", f"http://localhost:{WEB_PORT}")

SESSION_MAX_AGE = 3600 * 24  # 24 hours

# Demo mode: when true, destructive operations (e.g. password change) are blocked.
# Set DEMO_MODE=true in .env to enable for public demo deployments.
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes", "on")