# backend/core/healthcheck.py
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from typing import Dict, Any
from ..core.database import Session, get_db
import logging
import redis
from ..core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """بررسی سلامت پایه سیستم"""
    return {"status": "ok"}

@router.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """بررسی سلامت اتصال به پایگاه داده"""
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        return {
            "status": "ok",
            "database": "connected",
            "test_query": result[0] == 1 if result else False
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/health/redis")
async def redis_health_check() -> Dict[str, Any]:
    """بررسی سلامت اتصال به Redis"""
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        ping = redis_client.ping()
        return {
            "status": "ok" if ping else "error",
            "redis": "connected" if ping else "disconnected"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "error",
            "redis": "disconnected",
            "error": str(e)
        }

@router.get("/health/full")
async def full_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """بررسی سلامت کامل سیستم"""
    checks = {
        "database": await db_health_check(db),
        "redis": await redis_health_check(),
        "system": {"status": "ok"}
    }
    
    overall_status = "ok"
    for check, result in checks.items():
        if result.get("status") != "ok":
            overall_status = "degraded"
            break
    
    return {
        "status": overall_status,
        "checks": jsonable_encoder(checks)
    }
