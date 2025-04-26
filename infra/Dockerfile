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
