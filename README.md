# ساختار پروژه: پلتفرم بازی آنلاین شرطی

بیایید ساختار پروژه را به صورت حرفه‌ای و ماژولار طراحی کنیم:

```
/gaming-platform
│
├── /backend
│   ├── /core                  # سرویس اصلی
│   │   ├── app.py             # فایل اصلی FastAPI
│   │   ├── models.py          # مدل‌های دیتابیس
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── crud.py            # عملیات دیتابیس
│   │   ├── auth.py            # احراز هویت
│   │   ├── database.py        # تنظیمات دیتابیس
│   │   └── config.py          # تنظیمات
│   │
│   ├── /game_engine           # موتور بازی
│   │   ├── crash.py           # بازی Crash
│   │   ├── hokm.py            # بازی حکم
│   │   └── base.py            # کلاس پایه بازی
│   │
│   ├── /payment_gateway       # درگاه پرداخت
│   │   ├── providers.py       # ارائه‌دهندگان پرداخت
│   │   └── service.py         # سرویس پرداخت
│   │
│   ├── /notification          # اطلاع‌رسانی
│   │   ├── email.py           # ارسال ایمیل
│   │   └── websocket.py       # اطلاع‌رسانی لحظه‌ای
│   │
│   └── /admin                 # پنل مدیریت
│       ├── routes.py          # مسیرهای مدیریتی
│       └── dashboard.py       # داشبورد مدیریت
│
├── /frontend                  # رابط کاربری
│   ├── /public
│   ├── /src
│   └── ...
│
├── /infra                     # زیرساخت
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── nginx.conf
│   └── ...
│
├── .env                       # تنظیمات محیط
├── requirements.txt           # نیازمندی‌های پایتون
├── Makefile                   # دستورات توسعه
└── README.md                  # مستندات پروژه
```

## فایل اول: `backend/core/database.py`

این فایل برای اتصال به دیتابیس و تنظیمات پایه است:

```python
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
```

برای ادامه ساخت فایل‌های دیگر لطفاً کلمه "ادامه" را ارسال کنید.
