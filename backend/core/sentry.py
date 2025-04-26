# backend/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def setup_sentry():
    """تنظیمات اولیه Sentry"""
    if not settings.SENTRY_DSN:
        logger.warning("Sentry DSN not configured, skipping setup")
        return
    
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=f"{settings.PROJECT_NAME}@{settings.VERSION}",
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration()
            ],
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            send_default_pii=True,
            debug=settings.DEBUG,
        )
        logger.info("Sentry initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {str(e)}")

def capture_exception(error: Exception, context: dict = None):
    """ثبت خطا در Sentry"""
    if not settings.SENTRY_DSN:
        return
    
    try:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_exception(error)
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {str(e)}")

def capture_message(message: str, level: str = "info", context: dict = None):
    """ثبت پیام در Sentry"""
    if not settings.SENTRY_DSN:
        return
    
    try:
        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level)
    except Exception as e:
        logger.error(f"Failed to capture message in Sentry: {str(e)}")

def add_breadcrumb(message: str, category: str = "default", data: dict = None):
    """اضافه کردن ردپا به Sentry"""
    if not settings.SENTRY_DSN:
        return
    
    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            data=data
        )
    except Exception as e:
        logger.error(f"Failed to add breadcrumb in Sentry: {str(e)}")
