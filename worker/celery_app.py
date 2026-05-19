import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "campaign_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Prague",
    enable_utc=True,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # Important: process one task at a time for throttling
    # CRITICAL for multi-worker + long-running campaigns:
    # Redis broker default visibility_timeout is 3600s (1h). Any task longer than
    # that gets REDELIVERED to another worker while the original is still running.
    # With task_acks_late=True that means two workers execute the same campaign.
    # Set this higher than the longest possible campaign runtime.
    broker_transport_options={"visibility_timeout": 43200},  # 12 hours
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["worker"])