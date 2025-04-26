# backend/core/celery_app.py
from celery import Celery
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "gaming_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "backend.tasks.email",
        "backend.tasks.payment",
        "backend.tasks.game"
    ]
)

# تنظیمات عمومی Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tehran",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

# تنظیمات Queue
celery_app.conf.task_routes = {
    "backend.tasks.email.*": {"queue": "email"},
    "backend.tasks.payment.*": {"queue": "payment"},
    "backend.tasks.game.*": {"queue": "game"}
}

# تنظیمات Beat برای کارهای زمان‌بندی شده
celery_app.conf.beat_schedule = {
    "check_pending_payments": {
        "task": "backend.tasks.payment.check_pending_payments",
        "schedule": 300.0,  # هر 5 دقیقه
    },
    "cleanup_old_games": {
        "task": "backend.tasks.game.cleanup_old_games",
        "schedule": 3600.0,  # هر ساعت
    },
    "send_daily_stats": {
        "task": "backend.tasks.email.send_daily_stats_email",
        "schedule": 86400.0,  # هر روز
    }
}

if __name__ == "__main__":
    celery_app.start()
