# backend/core/event_handlers.py
from fastapi import FastAPI
from typing import Callable, Awaitable, Any
from contextlib import asynccontextmanager
from ..core.database import create_db_and_tables
from ..core.logging_config import setup_logging
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

async def startup_event_handler(app: FastAPI) -> None:
    """هندلر اجرایی هنگام راه‌اندازی برنامه"""
    logger.info("Application startup initiated")
    
    # ایجاد جداول دیتابیس
    await create_db_and_tables()
    logger.info("Database tables verified/created")
    
    # راه‌اندازی سرویس‌های پس‌زمینه
    if not settings.DEBUG:
        from ..core.celery_app import celery_app
        celery_app.conf.broker_connection_retry_on_startup = True
        logger.info("Background services initialized")
    
    logger.info("Application startup completed")

async def shutdown_event_handler(app: FastAPI) -> None:
    """هندلر اجرایی هنگام خاموشی برنامه"""
    logger.info("Application shutdown initiated")
    
    # توقف سرویس‌های پس‌زمینه
    if not settings.DEBUG:
        from ..core.celery_app import celery_app
        celery_app.close()
        logger.info("Background services stopped")
    
    logger.info("Application shutdown completed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات برنامه"""
    # راه‌اندازی
    setup_logging()
    await startup_event_handler(app)
    
    yield
    
    # خاموشی
    await shutdown_event_handler(app)

def register_event_handlers(app: FastAPI) -> None:
    """ثبت هندلرهای رویداد در برنامه FastAPI"""
    
    # رویدادهای کاربردی
    @app.on_event("startup")
    async def on_startup():
        await startup_event_handler(app)
    
    @app.on_event("shutdown")
    async def on_shutdown():
        await shutdown_event_handler(app)
    
    # رویدادهای سفارشی
    app.add_event_handler("game_started", game_event_handler)
    app.add_event_handler("transaction_processed", transaction_event_handler)
    app.add_event_handler("user_registered", user_event_handler)

async def game_event_handler(game_id: str, event_type: str) -> None:
    """هندلر رویدادهای بازی"""
    from ..core.database import SessionLocal
    from ..game_engine.base import GameFactory
    
    db = SessionLocal()
    try:
        game_engine = GameFactory.create_game(None, db, game_id)
        
        if event_type == "game_started":
            logger.info(f"Game {game_id} started")
            # ارسال نوتیفیکیشن به کاربران
            await game_engine.broadcast({
                "type": "game_start_notification",
                "game_id": game_id,
                "message": "Game has started"
            })
            
        elif event_type == "game_ended":
            logger.info(f"Game {game_id} ended")
            # ارسال نتایج به کاربران
            await game_engine.broadcast({
                "type": "game_end_notification",
                "game_id": game_id,
                "message": "Game has ended"
            })
            
    except Exception as e:
        logger.error(f"Error handling game event: {str(e)}")
    finally:
        db.close()

async def transaction_event_handler(transaction_id: str, event_type: str) -> None:
    """هندلر رویدادهای تراکنش"""
    from ..core.database import SessionLocal
    from ..notification.email import EmailService
    
    db = SessionLocal()
    try:
        transaction = db.query(models.Transaction).filter(
            models.Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return
        
        user = db.query(models.User).filter(
            models.User.id == transaction.user_id
        ).first()
        
        if event_type == "deposit_completed":
            logger.info(f"Deposit completed for user {user.id}")
            # ارسال ایمیل تایید واریز
            email_service = EmailService()
            await email_service.send_email(
                email_to=user.email,
                subject="Deposit Completed",
                body=f"Your deposit of {transaction.amount} has been processed"
            )
            
        elif event_type == "withdrawal_requested":
            logger.info(f"Withdrawal requested by user {user.id}")
            # ارسال ایمیل درخواست برداشت
            email_service = EmailService()
            await email_service.send_email(
                email_to=settings.ADMIN_EMAIL,
                subject="Withdrawal Request",
                body=f"User {user.username} requested a withdrawal of {transaction.amount}"
            )
            
    except Exception as e:
        logger.error(f"Error handling transaction event: {str(e)}")
    finally:
        db.close()

async def user_event_handler(user_id: str, event_type: str) -> None:
    """هندلر رویدادهای کاربر"""
    from ..core.database import SessionLocal
    from ..notification.email import EmailService
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.id == user_id
        ).first()
        
        if not user:
            logger.warning(f"User {user_id} not found")
            return
        
        if event_type == "user_registered":
            logger.info(f"New user registered: {user.username}")
            # ارسال ایمیل خوش‌آمدگویی
            email_service = EmailService()
            await email_service.send_welcome_email(
                email_to=user.email,
                username=user.username
            )
            
        elif event_type == "user_verified":
            logger.info(f"User verified: {user.username}")
            # ارسال ایمیل تایید حساب
            email_service = EmailService()
            await email_service.send_email(
                email_to=user.email,
                subject="Account Verified",
                body="Your account has been successfully verified"
            )
            
    except Exception as e:
        logger.error(f"Error handling user event: {str(e)}")
    finally:
        db.close()
