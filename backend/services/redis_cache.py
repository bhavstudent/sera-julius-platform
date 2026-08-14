"""
Redis Cache Service - Caching and session management
"""
import os
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
# Try to import Redis, fallback if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
# Import config - use environment variables as fallback
try:
    from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
except ImportError:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
logger = logging.getLogger(__name__)
# Redis client instance
_redis_client = None
async def init_redis():
    """Initialize Redis connection."""
    global _redis_client
    if not REDIS_AVAILABLE:
        logger.warning("[REDIS] redis package not installed. Using in-memory cache.")
        return None
    try:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        # Test connection
        await _redis_client.ping()
        logger.info(f"[REDIS] Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return _redis_client
    except Exception as e:
        logger.warning(f"[REDIS] Could not connect to Redis: {e}. Using in-memory cache.")
        _redis_client = None
        return None
async def close_redis():
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        try:
            await _redis_client.close()
        except Exception:
            pass
        _redis_client = None
def get_redis_client():
    """Get Redis client instance."""
    return _redis_client
class CacheService:
    """Cache service with Redis or in-memory fallback."""
    def __init__(self):
        self._memory_cache: Dict[str, tuple] = {}
        self._client = None
    async def get_client(self):
        if not self._client:
            self._client = await init_redis()
        return self._client
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        client = await self.get_client()
        if client:
            try:
                value = await client.get(key)
                if value:
                    return json.loads(value)
                return None
            except Exception:
                pass
        # In-memory fallback
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if expiry and datetime.now() > expiry:
                del self._memory_cache[key]
                return None
            return value
        return None
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (seconds)."""
        client = await self.get_client()
        if client:
            try:
                await client.setex(key, ttl, json.dumps(value))
                return
            except Exception:
                pass
        # In-memory fallback
        expiry = datetime.now() + timedelta(seconds=ttl) if ttl else None
        self._memory_cache[key] = (value, expiry)
    async def delete(self, key: str):
        """Delete value from cache."""
        client = await self.get_client()
        if client:
            try:
                await client.delete(key)
            except Exception:
                pass
        if key in self._memory_cache:
            del self._memory_cache[key]
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        client = await self.get_client()
        if client:
            try:
                return await client.exists(key) > 0
            except Exception:
                pass
        return key in self._memory_cache
# Singleton instance
cache_service = CacheService()
async def get_cached_data(key: str) -> Optional[Any]:
    """Get data from cache."""
    return await cache_service.get(key)
async def set_cached_data(key: str, data: Any, ttl: int = 3600):
    """Set data in cache."""
    await cache_service.set(key, data, ttl)
async def invalidate_cache(key: str):
    """Invalidate cache key."""
    await cache_service.delete(key)
