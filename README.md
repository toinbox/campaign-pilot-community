<p align="center">
  <h1 align="center">Campaign Pilot — Community Edition</h1>
  <p align="center">
    Self-hosted SMTP engine with intelligent throttling and multi-server rotation.
  </p>
</p>

<p align="center">
  <a href="https://github.com/toinbox/campaign-pilot/blob/community/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.12-brightgreen.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/docker--compose-ready-2496ED.svg?logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/redis-7-DC382D.svg?logo=redis&logoColor=white" alt="Redis 7">
</p>

---

Campaign Pilot is a high-performance, developer-centric email orchestration engine built with **FastAPI**, **Celery**, and **Redis**. It gives you absolute control over your sending infrastructure — without the limitations and costs of standard SaaS platforms.

## Key Features

- **Intelligent SMTP Throttling** — Atomic hourly and daily limits per SMTP server and per recipient domain enforced via Redis Lua scripts. Configurable rate limits per target domain protect your sender reputation.
- **Domain Reputation Protection** — Automatic detection of domain-level blocks and reputation issues. If a recipient domain returns a negative reputation signal, it is automatically blocked to prevent further deliverability damage.
- **Multi-Server Pool** — Unlimited SMTP servers with Round-Robin, Batch, or Weighted rotation strategies.
- **IP Warmup System** — Automated exponential escalation of daily sending limits for new servers.
- **IMAP Bounce Scrubber** — Automated RFC 3464 DSN parsing to keep your recipient lists clean.
- **Multilingual UI** — Fully translated into English, Czech, German, Russian, and Spanish.
- **Dockerized Deployment** — Production-ready in minutes via `docker-compose`.

## Tech Stack

| Component   | Technology                |
|-------------|---------------------------|
| Backend     | FastAPI (Python 3.12)     |
| Task Queue  | Celery + Redis 7          |
| Database    | SQLite (WAL mode)         |
| Email Editor| TinyMCE 6 + MJML          |
| Environment | Docker & Docker Compose   |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) ≥ 20.10
- [Docker Compose](https://docs.docker.com/compose/install/) ≥ 2.0
- At least one SMTP server for sending

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/toinbox/campaign-pilot.git
cd campaign-pilot

# 2. Configure environment
cp env.example .env
# Edit .env with your settings (see Environment Variables below)

# 3. Build and start
docker compose up --build -d

# 4. Open the dashboard
# http://localhost:8080
# Default credentials — user: admin / password: admin
```

> **⚠️ Important:** Change the Profile default `ADMIN_PASSWORD` and `SECRET_KEY` in `.env` before deploying to production.

> **Local development (without Docker):** Run `./install_tinymce.sh` from the project root to install the TinyMCE editor. Docker builds handle this automatically.

## Environment Variables

| Variable         | Description                              | Default                     |
|------------------|------------------------------------------|-----------------------------|
| `APP_NAME`       | Application display name                 | `CampaignPilot`             |
| `DEMO_MODE`      | Enable demo mode (read-only)             | `false`                     |
| `SECRET_KEY`     | Secret key for session signing           | *(generate your own)*       |
| `ADMIN_USER`     | Admin username                           | `admin`                     |
| `ADMIN_PASSWORD` | Admin password                           | `admin`                     |
| `TZ`             | Timezone                                 | `Europe/Prague`             |
| `DB_PATH`        | SQLite database path inside container    | `/data/campaign_manager.db` |
| `REDIS_URL`      | Redis connection URL                     | `redis://redis:6379/0`      |
| `WEB_HOST`       | Web server bind address                  | `0.0.0.0`                   |
| `WEB_PORT`       | Web server port                          | `8080`                      |
| `APP_BASE_URL`   | Public URL of the application            | `http://yourdomain.com`     |

## Running Multiple Campaigns

The default `docker-compose.yml` starts Celery with `--concurrency=2`, which supports **one campaign at a time** (each campaign uses 2 worker slots). To run multiple campaigns simultaneously, increase the concurrency value in the worker service command:

```yaml
# docker-compose.yml — worker service
command: celery -A worker.celery_app worker --beat --loglevel=info --concurrency=4
```

| Concurrency | Simultaneous Campaigns |
|:-----------:|:----------------------:|
| 2           | 1                      |
| 4           | 2                      |
| 6           | 3                      |
| 8           | 4                      |

> **Note:** Higher concurrency uses more RAM and CPU. Monitor your server resources when increasing this value.

## Project Structure

```
campaign-pilot/
├── app/                  # FastAPI application (routes, models, templates)
├── worker/               # Celery worker (SMTP sending, bounce scrubbing)
├── geoip/                # GeoIP data for geo-based analytics
├── Dockerfile            # Container build instructions
├── docker-compose.yml    # Service orchestration
├── entrypoint.sh         # Container startup (auto-installs TinyMCE)
├── requirements.txt      # Python dependencies
├── install_tinymce.sh    # TinyMCE install for local dev without Docker
├── env.example           # Environment variable template
├── LICENSE               # MIT License
└── README.md
```

## Full Version

This Community Edition includes the core SMTP sending engine. The **[Full Version](https://mailtoinbox.vip)** adds a second sending engine (Pool Mode), advanced deliverability tools, and campaign analytics.

### Sending Engine

| Feature | Community | Full |
|---|:---:|:---:|
| SMTP server pool (Round-Robin, Weighted, Batch) | ✅ | ✅ |
| Per-server & per-domain hourly/daily limits | ✅ | ✅ |
| IP Warmup with exponential escalation | ✅ | ✅ |
| Pool Mode — sending via personal email accounts | — | ✅ |
| 1:1 Desktop Client MIME simulation | — | ✅ |
| Per-account SOCKS4/5 proxy support | — | ✅ |
| Rolling 24h window throttling (no midnight reset) | — | ✅ |

### Deliverability & Anti-Fingerprinting

| Feature | Community | Full |
|---|:---:|:---:|
| IMAP Bounce Scrubber (RFC 3464 DSN) | ✅ | ✅ |
| Domain reputation protection & auto-blocking | ✅ | ✅ |
| Spin System (up to 7 message variations) | — | ✅ |
| Shuffle Deck rotation per account | — | ✅ |
| Nested Spintax engine | — | ✅ |
| HTML structural noise (unique per email) | — | ✅ |
| Link uniquification | — | ✅ |
| Preheader generation | ✅ | ✅ |
| Bridge URL via Cloudflare Workers | — | ✅ |

### Automation & Analytics

| Feature | Community | Full |
|---|:---:|:---:|
| Campaign scheduling | ✅ | ✅ |
| Autopilot — automatic reputation building | — | ✅ |
| Night pause with biorhythm simulation | — | ✅ |
| Scoring — reply detection & campaign analytics | — | ✅ |
| Scoring export (Markdown reports) | — | ✅ |

### Contact & Account Management

| Feature | Community | Full |
|---|:---:|:---:|
| CSV import with field mapping | ✅ | ✅ |
| Contact lists with status tracking | ✅ | ✅ |
| GeoIP country detection | ✅ | ✅ |
| MX email validation | ✅ | ✅ |
| Pool account inbox (read, reply, delete, move) | — | ✅ |
| Multi-provider support (10+ providers) | — | ✅ |
| Pool account health monitoring | — | ✅ |

### General

| Feature | Community | Full |
|---|:---:|:---:|
| Multilingual UI (EN, CS, DE, RU, ES) | ✅ | ✅ |
| Docker deployment | ✅ | ✅ |
| Open-tracking & click-tracking (SMTP) | ✅ | ✅ |
| Full data sovereignty — everything in your container | ✅ | ✅ |

🔗 **Try it live:** [cp.mailtoinbox.vip](https://cp.mailtoinbox.vip) (user: `admin` / password: `demo`)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
