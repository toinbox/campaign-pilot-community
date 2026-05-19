<p align="center">
  <h1 align="center">Campaign Pilot — Community Edition</h1>
  <p align="center">
    Self-hosted SMTP engine with intelligent throttling and multi-server rotation.
  </p>
</p>

<p align="center">
  <a href="https://github.com/toinbox/campaign-pilot/blob/community/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-brightgreen.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/docker--compose-ready-2496ED.svg?logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/redis-7-DC382D.svg?logo=redis&logoColor=white" alt="Redis 7">
</p>

---

Campaign Pilot is a high-performance, developer-centric email orchestration engine built with **FastAPI**, **Celery**, and **Redis**. It gives you absolute control over your sending infrastructure — without the limitations and costs of standard SaaS platforms.

## Key Features

- **Intelligent SMTP Throttling** — Atomic hourly and daily limits per SMTP server and per recipient domain (Gmail, Outlook, Yahoo, etc.) enforced via Redis Lua scripts.
- **Multi-Server Pool** — Unlimited SMTP servers with Round-Robin, Batch, or Weighted rotation strategies.
- **IP Warmup System** — Automated exponential escalation of daily sending limits for new servers.
- **IMAP Bounce Scrubber** — Automated RFC 3464 DSN parsing to keep your recipient lists clean.
- **Multilingual UI** — Fully translated into English, Czech, German, Russian, and Spanish.
- **Dockerized Deployment** — Production-ready in minutes via `docker-compose`.

## Tech Stack

| Component   | Technology                |
|-------------|---------------------------|
| Backend     | FastAPI (Python 3.10+)    |
| Task Queue  | Celery + Redis 7          |
| Database    | SQLite (WAL mode)         |
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
cp .env.example .env
# Edit .env with your settings (see Environment Variables below)

# 3. Build and start
docker-compose up --build -d

# 4. Open the dashboard
# http://localhost:8080
# Default credentials — user: admin / password: admin
```

> **⚠️ Important:** Change the default `ADMIN_PASSWORD` and `SECRET_KEY` in `.env` before deploying to production.

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

## Project Structure

```
campaign-pilot/
├── app/                  # FastAPI application (routes, models, templates)
├── worker/               # Celery worker (SMTP sending, bounce scrubbing)
├── geoip/                # GeoIP data for geo-based analytics
├── Dockerfile            # Container build instructions
├── docker-compose.yml    # Service orchestration
├── requirements.txt      # Python dependencies
├── env.example           # Environment variable template
├── LICENSE               # MIT License
└── README.md
```

## Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please make sure your code follows the existing style and includes appropriate tests where applicable.

## Security

If you discover a security vulnerability, please **do not** open a public issue. Instead, contact us directly at the email listed in our GitHub profile. We take security seriously and will respond promptly.

## Stealth Edition

Need advanced capabilities like 1:1 Desktop Client Simulation, Personal Account Pools, Autopilot Warm-up, or Deliverability Scoring? Check out the **[Stealth Edition](https://mailtoinbox.vip)**.

A live demo is available at [cp.mailtoinbox.vip](https://cp.mailtoinbox.vip) (user: `admin` / password: `demo`).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
