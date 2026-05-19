# Campaign Pilot — Community Edition

**Self-hosted SMTP engine with intelligent throttling and multi-server rotation.**

Campaign Pilot is a high-performance, developer-centric email orchestration engine built with **FastAPI, Celery, and Redis**. It is designed for those who need absolute control over their sending infrastructure and want to avoid the limitations and high costs of standard SaaS platforms.

## 🚀 Key Features
* **Intelligent SMTP Throttling:** Atomic hourly and daily limits per SMTP server and per recipient domain (Gmail, Outlook, etc.) using Redis Lua scripts.
* **Multi-Server Pool:** Support for unlimited SMTP servers with Round-Robin, Batch, or Weighted rotation strategies.
* **IP Warmup System:** Automated exponential escalation of daily limits for new servers.
* **IMAP Bounce Scrubber:** Automated RFC 3464 DSN parsing to keep your lists clean.
* **Multilingual UI:** Fully translated into English, Czech, German, Russian, and Spanish.
* **Dockerized:** Ready to deploy in minutes via `docker-compose`.

## 🛠 Tech Stack
* **Backend:** FastAPI (Python 3.10+)
* **Task Queue:** Celery + Redis 7
* **Database:** SQLite (WAL mode)
* **Environment:** Docker & Docker Compose

## 📦 Quick Start
1. Clone this repository.
2. Copy `.env.example` to `.env` and fill in your details.
3. Run `docker-compose build up -d`
4. Access the dashboard at `http://localhost:8080`
5. Defualt user:admin passord:admin

---

## 🛡️ Need Stealth Features?
If you require **1:1 Desktop Client Simulation**, **Personal Account Pools (Pool Mode)**, **Autopilot (Warm-up)**, or **Advanced Scoring**, check out our **Stealth Edition** at [MailToInbox.vip](https://mailtoinbox.vip).
Demo version : https://cp.mailtoinbox.vip
user:admin password:demo

## License
MIT License - see LICENSE file for details.
