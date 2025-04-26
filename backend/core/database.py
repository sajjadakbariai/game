# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings

# URL اتصال به دیتابیس از تنظیمات محیطی می‌آید
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    تابع برای ایجاد session دیتابیس
    در هر درخواست یک session جدید ایجاد می‌کند
    و پس از اتمام درخواست آن را می‌بندد
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
