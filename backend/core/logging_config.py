# backend/core/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from ..core.config import settings

def setup_logging():
    """تنظیمات پایه برای سیستم لاگ‌گیری"""
    
    # ایجاد دایرکتوری لاگ‌ها اگر وجود نداشته باشد
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # فرمت مشترک برای تمام لاگ‌ها
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # تنظیمات سطح کلی لاگ
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Handler برای کنسول
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler برای فایل لاگ اصلی
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # لاگ‌های مخصوص خطاها
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # لاگ‌های مخصوص درخواست‌ها
    access_log = logging.getLogger('access')
    access_log.setLevel(logging.INFO)
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=1024 * 1024 * 10,  # 10 MB
        backupCount=3
    )
    access_handler.setFormatter(formatter)
    access_log.addHandler(access_handler)
    access_log.propagate = False
    
    # لاگ‌های مخصوص پایگاه داده
    db_log = logging.getLogger('sqlalchemy')
    db_log.setLevel(logging.WARNING)
    db_handler = RotatingFileHandler(
        'logs/db.log',
        maxBytes=1024 * 1024 * 2,  # 2 MB
        backupCount=2
    )
    db_handler.setFormatter(formatter)
    db_log.addHandler(db_handler)
    
    # تنظیم سطح لاگ بر اساس محیط اجرا
    if settings.DEBUG:
        root_logger.setLevel(logging.DEBUG)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.INFO)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
