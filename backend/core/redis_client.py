# backend/core/redis_client.py
import redis
from redis.asyncio import Redis as AsyncRedis
from ..core.config import settings
import logging
from typing import Optional, Any, Union

logger = logging.getLogger(__name__)

class RedisClient:
    """کلاس مدیریت اتصال به Redis"""
    
    _instance = None
    _async_instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.sync_client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            cls._instance.async_client = AsyncRedis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            
            # تست اتصال
            try:
                cls._instance.sync_client.ping()
                logger.info("Connected to Redis (sync)")
            except Exception as e:
                logger.error(f"Failed to connect to Redis (sync): {str(e)}")
                raise
            
        return cls._instance
    
    @classmethod
    async def get_async_client(cls) -> AsyncRedis:
        """دریافت کلاینت ناهمگون Redis"""
        if cls._async_instance is None:
            cls._async_instance = AsyncRedis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            try:
                await cls._async_instance.ping()
                logger.info("Connected to Redis (async)")
            except Exception as e:
                logger.error(f"Failed to connect to Redis (async): {str(e)}")
                raise
        return cls._async_instance
    
    @staticmethod
    def get_sync_client() -> redis.Redis:
        """دریافت کلاینت همگون Redis"""
        return RedisClient().sync_client
    
    @staticmethod
    async def set(
        key: str, 
        value: Union[str, bytes, int, float],
        expire: Optional[int] = None
    ) -> bool:
        """ذخیره مقدار در Redis (ناهمگون)"""
        client = await RedisClient.get_async_client()
        try:
            if expire:
                return await client.setex(key, expire, value)
            return await client.set(key, value)
        except Exception as e:
            logger.error(f"Redis set failed: {str(e)}")
            raise
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """دریافت مقدار از Redis (ناهمگون)"""
        client = await RedisClient.get_async_client()
        try:
            return await client.get(key)
        except Exception as e:
            logger.error(f"Redis get failed: {str(e)}")
            raise
    
    @staticmethod
    def sync_set(
        key: str, 
        value: Union[str, bytes, int, float],
        expire: Optional[int] = None
    ) -> bool:
        """ذخیره مقدار در Redis (همگون)"""
        client = RedisClient.get_sync_client()
        try:
            if expire:
                return client.setex(key, expire, value)
            return client.set(key, value)
        except Exception as e:
            logger.error(f"Redis sync_set failed: {str(e)}")
            raise
    
    @staticmethod
    def sync_get(key: str) -> Optional[Any]:
        """دریافت مقدار از Redis (همگون)"""
        client = RedisClient.get_sync_client()
        try:
            return client.get(key)
        except Exception as e:
            logger.error(f"Redis sync_get failed: {str(e)}")
            raise
    
    @staticmethod
    async def publish(channel: str, message: str) -> int:
        """انتشار پیام در کانال Redis"""
        client = await RedisClient.get_async_client()
        try:
            return await client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish failed: {str(e)}")
            raise
    
    @staticmethod
    async def subscribe(channel: str):
        """اشتراک در کانال Redis"""
        client = await RedisClient.get_async_client()
        pubsub = client.pubsub()
        try:
            await pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.error(f"Redis subscribe failed: {str(e)}")
            raise
    
    @staticmethod
    async def delete(key: str) -> int:
        """حذف کلید از Redis"""
        client = await RedisClient.get_async_client()
        try:
            return await client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete failed: {str(e)}")
            raise
    
    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """افزایش مقدار عددی در Redis"""
        client = await RedisClient.get_async_client()
        try:
            return await client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment failed: {str(e)}")
            raise
    
    @staticmethod
    async def expire(key: str, seconds: int) -> bool:
        """تنظیم زمان انقضا برای کلید"""
        client = await RedisClient.get_async_client()
        try:
            return await client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire failed: {str(e)}")
            raise
