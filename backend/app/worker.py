"""
Celery worker for async task processing.
Start with: celery -A app.worker worker --loglevel=info
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "placement_intel",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=30,
    task_max_retries=3,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
