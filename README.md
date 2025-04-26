# ساختار پروژه: پلتفرم بازی آنلاین شرطی

# Gaming Platform

پلتفرم بازی آنلاین شرطی با امتیاز و کیف‌پول

## ویژگی‌های اصلی

- سیستم کاربری و احراز هویت
- کیف پول با امکان واریز و برداشت
- بازی‌های مختلف (انفجار، حکم، پوکر)
- سیستم اطلاع‌رسانی لحظه‌ای
- پنل مدیریت

## راه‌اندازی

### پیش‌نیازها

- Docker
- Docker Compose

### نصب

1. کپی فایل env نمونه:
   ```bash
   cp .env.example .env











# فایل چهاردهم: `infra/Dockerfile`

این فایل برای ساخت image داکر برای سرویس backend استفاده می‌شود:

```dockerfile
# infra/Dockerfile
FROM python:3.9-slim as builder

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim

WORKDIR /app

# کپی وابستگی‌های نصب شده از مرحله builder
COPY --from=builder /root/.local /root/.local
COPY . .

# اضافه کردن مسیر pip به PATH
ENV PATH=/root/.local/bin:$PATH

# کد اصلی برنامه
COPY ./backend /app/backend

# پورت مورد استفاده
EXPOSE 8000

# دستور اجرای برنامه
CMD ["uvicorn", "backend.core.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

# فایل پانزدهم: `infra/nginx.conf`

این فایل پیکربندی Nginx برای پروکسی کردن درخواست‌ها به backend و سرویس دادن فایل‌های frontend:

```nginx
# infra/nginx.conf
events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 20M;

    # تنظیمات upstream برای backend
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # مسیرهای API به backend پروکسی می‌شوند
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # مسیرهای WebSocket
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # فایل‌های static و frontend
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # خطاها
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root html;
        }
    }
}
```

# فایل شانزدهم: `Makefile`

این فایل برای اجرای دستورات رایج توسعه استفاده می‌شود:

```makefile
# Makefile
.PHONY: up down build rebuild logs backend-logs db-logs redis-logs test migrate

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

rebuild:
	docker-compose down && docker-compose up -d --build

logs:
	docker-compose logs -f

backend-logs:
	docker-compose logs -f backend

db-logs:
	docker-compose logs -f db

redis-logs:
	docker-compose logs -f redis

test:
	docker-compose exec backend pytest -v

migrate:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend bash

db-shell:
	docker-compose exec db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) $$(grep POSTGRES_DB .env | cut -d '=' -f2)

format:
	docker-compose exec backend black .
	docker-compose exec backend isort .

lint:
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check .
	docker-compose exec backend flake8 .
```

# فایل هفدهم: `requirements.txt`

این فایل شامل تمام وابستگی‌های پایتون پروژه می‌شود:

```text
# requirements.txt
fastapi==0.95.0
uvicorn==0.21.1

# دیتابیس
sqlalchemy==2.0.9
psycopg2-binary==2.9.5
alembic==1.10.2
asyncpg==0.27.0

# احراز هویت
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.0.1

# اعتبارسنجی
pydantic==1.10.7
email-validator==1.3.1

# توسعه
python-dotenv==1.0.0
black==23.3.0
isort==5.12.0
flake8==6.0.0
pytest==7.3.1
pytest-asyncio==0.21.0

# سایر
redis==4.5.4
httpx==0.24.0
python-multipart==0.0.6
```

# فایل هجدهم: `README.md`

این فایل شامل راهنمای راه‌اندازی و استفاده از پروژه می‌شود:

```markdown
# Gaming Platform

پلتفرم بازی آنلاین شرطی با امتیاز و کیف‌پول

## ویژگی‌های اصلی

- سیستم کاربری و احراز هویت
- کیف پول با امکان واریز و برداشت
- بازی‌های مختلف (انفجار، حکم، پوکر)
- سیستم اطلاع‌رسانی لحظه‌ای
- پنل مدیریت

## راه‌اندازی

### پیش‌نیازها

- Docker
- Docker Compose

### نصب

1. کپی فایل env نمونه:
   ```bash
   cp .env.example .env
   ```

2. ویرایش فایل .env با مقادیر مناسب

3. ساخت و راه‌اندازی کانتینرها:
   ```bash
   make up
   ```

4. اجرای migrations:
   ```bash
   make migrate
   ```

### دستورات مفید

- راه‌اندازی سیستم: `make up`
- توقف سیستم: `make down`
- بازسازی کانتینرها: `make rebuild`
- مشاهده لاگ‌ها: `make logs`
- اجرای تست‌ها: `make test`
- فرمت کد: `make format`

## معماری سیستم

سیستم به صورت میکروسرویس طراحی شده است:

- **Core Service**: مدیریت کاربران، احراز هویت، کیف پول
- **Game Engine**: مدیریت بازی‌ها و منطق بازی
- **Payment Gateway**: پرداخت‌ها و تراکنش‌ها
- **Admin Panel**: مدیریت سیستم
- **Notification Service**: اطلاع‌رسانی به کاربران

## API Documentation

مستندات API پس از راه‌اندازی در آدرس‌های زیر قابل دسترسی است:

- Swagger UI: http://localhost/api/docs
- ReDoc: http://localhost/api/redoc
```

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
