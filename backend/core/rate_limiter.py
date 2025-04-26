# backend/core/rate_limiter.py
from typing import Optional, Tuple
from datetime import timedelta
from .redis_client import RedisClient
from .config import settings
import time
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """سیستم محدودیت نرخ درخواست"""
    
    def __init__(
        self, 
        redis_prefix: str = "rate_limit",
        default_limit: int = 100,
        default_window: int = 60  # ثانیه
    ):
        self.redis_prefix = redis_prefix
        self.default_limit = default_limit
        self.default_window = default_window
    
    async def check_rate_limit(
        self, 
        identifier: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, dict]:
        """
        بررسی محدودیت نرخ درخواست
        
        Returns:
            tuple: (is_allowed, headers)
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        
        key = f"{self.redis_prefix}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window
        
        try:
            # استفاده از Lua script برای اتمیک بودن عملیات
            lua_script = """
            local key = KEYS[1]
            local now = tonumber(ARGV[1])
            local window_start = tonumber(ARGV[2])
            local limit = tonumber(ARGV[3])
            
            -- حذف درخواست‌های خارج از پنجره زمانی
            redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
            
            -- شمارش درخواست‌های فعلی
            local current_count = redis.call('ZCARD', key)
            
            if current_count < limit then
                -- افزودن درخواست جدید
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, ARGV[4])
                return {1, limit - current_count - 1}
            else
                -- محاسبه زمان باقیمانده تا آزاد شدن محدودیت
                local oldest_request = redis.call('ZRANGE', key, 0, 0)[1]
                local reset_time = window_start + ARGV[4] - tonumber(oldest_request)
                return {0, reset_time}
            end
            """
            
            result = await RedisClient.get_async_client().eval(
                lua_script,
                1,  # تعداد کلیدها
                key,
                current_time,
                window_start,
                limit,
                window
            )
            
            allowed = bool(result[0])
            remaining = result[1]
            
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(window_start + window)
            }
            
            return allowed, headers
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # در صورت خطا، اجازه دسترسی داده می‌شود
            return True, {}
    
    async def middleware(
        self, 
        request,
        call_next,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ):
        """میدلور برای محدودیت نرخ درخواست"""
        # شناسه کاربر (IP یا user_id)
        identifier = request.client.host
        if hasattr(request.state, "user") and request.state.user:
            identifier = str(request.state.user.id)
        
        allowed, headers = await self.check_rate_limit(
            identifier,
            limit,
            window
        )
        
        if not allowed:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers=headers
            )
        
        response = await call_next(request)
        
        # اضافه کردن هدرهای RateLimit به پاسخ
        for header, value in headers.items():
            response.headers[header] = str(value)
        
        return response

# نمونه پیش‌فرض برای استفاده در سراسر برنامه
rate_limiter = RateLimiter(
    redis_prefix=f"{settings.PROJECT_NAME}:rate_limit",
    default_limit=settings.RATE_LIMIT_DEFAULT,
    default_window=settings.RATE_LIMIT_WINDOW
)
