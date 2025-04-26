# backend/core/cache.py
from typing import Optional, Any, Callable, TypeVar, Coroutine
from functools import wraps
import pickle
import hashlib
import json
from datetime import timedelta
from .redis_client import RedisClient
from .config import settings
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheManager:
    """مدیریت سیستم کش با Redis"""
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """تولید کلید کش منحصر به فرد بر اساس آرگومان‌ها"""
        arg_str = json.dumps(args, sort_keys=True)
        kwarg_str = json.dumps(kwargs, sort_keys=True)
        hash_input = f"{arg_str}:{kwarg_str}".encode()
        return hashlib.md5(hash_input).hexdigest()
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """دریافت مقدار از کش"""
        try:
            cached_data = await RedisClient.get(key)
            if cached_data:
                return pickle.loads(cached_data.encode('latin1'))
            return None
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None
    
    @staticmethod
    async def set(
        key: str, 
        value: Any, 
        ttl: Optional[timedelta] = None
    ) -> bool:
        """ذخیره مقدار در کش"""
        try:
            serialized = pickle.dumps(value).decode('latin1')
            expire_seconds = int(ttl.total_seconds()) if ttl else None
            return await RedisClient.set(key, serialized, expire_seconds)
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """حذف مقدار از کش"""
        try:
            return await RedisClient.delete(key) > 0
        except Exception as e:
            logger.error(f"Cache delete failed: {str(e)}")
            return False
    
    @staticmethod
    async def clear_namespace(namespace: str) -> int:
        """پاکسازی تمام کلیدهای یک namespace"""
        try:
            keys = await RedisClient.keys(f"{namespace}:*")
            if keys:
                return await RedisClient.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache namespace clear failed: {str(e)}")
            return 0
    
    @staticmethod
    def cached(
        ttl: Optional[timedelta] = None,
        namespace: Optional[str] = None,
        key_func: Optional[Callable[..., str]] = None
    ):
        """دکوراتور برای کش کردن نتیجه تابع"""
        
        def decorator(func: Callable[..., Coroutine[Any, Any, T]]):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                # تولید کلید کش
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    base_key = f"{func.__module__}:{func.__name__}"
                    arg_key = CacheManager.generate_cache_key(*args, **kwargs)
                    cache_key = f"{base_key}:{arg_key}"
                
                if namespace:
                    cache_key = f"{namespace}:{cache_key}"
                
                # بررسی وجود در کش
                cached_result = await CacheManager.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_result
                
                # اجرای تابع اصلی در صورت عدم وجود در کش
                result = await func(*args, **kwargs)
                
                # ذخیره نتیجه در کش
                await CacheManager.set(cache_key, result, ttl)
                logger.debug(f"Cache set for key: {cache_key}")
                
                return result
            
            return wrapper
        
        return decorator
    
    @staticmethod
    async def invalidate(*keys: str) -> None:
        """باطل کردن کش برای کلیدهای مشخص"""
        for key in keys:
            try:
                await CacheManager.delete(key)
                logger.debug(f"Cache invalidated for key: {key}")
            except Exception as e:
                logger.error(f"Cache invalidation failed for key {key}: {str(e)}")

# نمونه پیش‌فرض برای استفاده در سراسر برنامه
cache = CacheManager()
