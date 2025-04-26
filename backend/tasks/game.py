# backend/tasks/game.py
from ..core.celery_app import celery_app
from ..core.database import SessionLocal
from ..core import models
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="start_scheduled_game")
def start_scheduled_game(game_id: str):
    """وظیفه شروع بازی زمان‌بندی شده"""
    db = SessionLocal()
    try:
        game = db.query(models.Game).filter(models.Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        # TODO: پیاده‌سازی منطق شروع بازی
        from ..game_engine.base import GameFactory
        game_engine = GameFactory.create_game(game.game_type, db, game.id)
        game_engine.start_game()
        
        return {"status": "success", "game_id": game_id}
    except Exception as e:
        logger.error(f"Failed to start game {game_id}: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(name="cleanup_old_games")
def cleanup_old_games():
    """وظیفه پاکسازی بازی‌های قدیمی"""
    db = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        # بازی‌های تکمیل شده قدیمی
        completed_games = db.query(models.Game).filter(
            models.Game.status == models.GameStatus.COMPLETED.value,
            models.Game.completed_at < cutoff_time
        ).all()
        
        # بازی‌های رها شده قدیمی
        abandoned_games = db.query(models.Game).filter(
            models.Game.status.in_([
                models.GameStatus.WAITING.value,
                models.GameStatus.ACTIVE.value
            ]),
            models.Game.created_at < cutoff_time
        ).all()
        
        # انجام عملیات پاکسازی
        for game in completed_games + abandoned_games:
            try:
                # TODO: می‌توانید لاگ‌های بازی را ذخیره کنید قبل از حذف
                db.delete(game)
            except Exception as e:
                logger.error(f"Failed to cleanup game {game.id}: {str(e)}")
                db.rollback()
        
        db.commit()
        return {
            "status": "success",
            "completed_games_cleaned": len(completed_games),
            "abandoned_games_cleaned": len(abandoned_games)
        }
    finally:
        db.close()

@celery_app.task(name="notify_game_start")
def notify_game_start(game_id: str):
    """وظیفه اطلاع‌رسانی شروع بازی"""
    db = SessionLocal()
    try:
        game = db.query(models.Game).filter(models.Game.id == game_id).first()
        if not game:
            raise ValueError("Game not found")
        
        # TODO: پیاده‌سازی منطق اطلاع‌رسانی
        # می‌توانید از سرویس WebSocket یا ایمیل استفاده کنید
        
        return {"status": "success", "game_id": game_id}
    except Exception as e:
        logger.error(f"Failed to notify game start {game_id}: {str(e)}")
        raise
    finally:
        db.close()
