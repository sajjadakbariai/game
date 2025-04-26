# backend/core/middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import time
from typing import Callable, Awaitable
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware برای محدود کردن نرخ درخواست‌ها"""
    
    def __init__(self, app, max_requests: int = 100, time_window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize request count for new IPs
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {
                'count': 1,
                'start_time': current_time
            }
        else:
            # Reset counter if time window has passed
            if current_time - self.request_counts[client_ip]['start_time'] > self.time_window:
                self.request_counts[client_ip] = {
                    'count': 1,
                    'start_time': current_time
                }
            else:
                self.request_counts[client_ip]['count'] += 1
        
        # Check if rate limit exceeded
        if self.request_counts[client_ip]['count'] > self.max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(self.time_window)}
            )
        
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware برای اضافه کردن هدرهای امنیتی"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # اضافه کردن هدرهای امنیتی
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware برای ثبت لاگ درخواست‌ها"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request: {request.method} {request.url} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.2f}s"
        )
        
        return response

async def db_session_middleware(request: Request, call_next):
    """Middleware برای مدیریت session دیتابیس"""
    from ..core.database import SessionLocal
    
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    
    return response
