# backend/core/config.py
from pydantic import BaseSettings, AnyHttpUrl, PostgresDsn
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    # تنظیمات پایه
    PROJECT_NAME: str = "Gaming Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 هفته
    
    # تنظیمات دیتابیس
    DATABASE_URL: PostgresDsn = "postgresql://user:password@localhost:5432/gaming_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    
    # تنظیمات CORS
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
    ]
    
    # تنظیمات پرداخت
    PAYMENT_PROVIDER: str = "zarinpal"  # یا "idpay", "parsian"
    PAYMENT_CALLBACK_URL: str = "http://localhost:8000/api/v1/payment/verify"
    MIN_DEPOSIT: float = 10000  # حداقل واریز (تومان)
    MIN_WITHDRAWAL: float = 100000  # حداقل برداشت (تومان)
    
    # تنظیمات بازی
    INITIAL_CREDIT: int = 100  # امتیاز اولیه کاربران
    MIN_GAME_STAKE: int = 10  # حداقل شرط در بازی‌ها
    MAX_GAME_STAKE: int = 10000  # حداکثر شرط در بازی‌ها
    
    # تنظیمات SMTP برای ایمیل
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = "noreply@gaming-platform.com"
    
    # تنظیمات WebSocket
    WS_MAX_CONNECTIONS: int = 1000
    WS_KEEPALIVE_INTERVAL: int = 30  # ثانیه
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
