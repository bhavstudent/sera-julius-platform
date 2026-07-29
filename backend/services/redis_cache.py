"""
SERA Platform — Redis Cache & Session Client
=============================================
Provides asynchronous Redis caching and session storage with graceful fallback to in-memory TTL caching
if Redis server is unavailable.
"""

import json
import logging
from typing import Any, Optional
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB

logger = logging.getLogger("sera.redis")

_redis_client = None
_in_memory_fallback = {}

async def init_redis() -> None:
    """Initialize Redis async client with fallback."""
    global _redis_client
    try:
        import redis.asyncio as aioredis
        client = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD or None,
            db=REDIS_DB,
            decode_responses=True,
            socket_timeout=2.0
        )
        await client.ping()
        _redis_client = client
        logger.info(f"[REDIS] Connected successfully to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        _redis_client = None
        logger.warning(f"[REDIS] Redis server unavailable ({e}). Using in-memory fallback cache.")

async def set_cache(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    """Set key in Redis cache (or in-memory fallback)."""
    val_str = json.dumps(value) if not isinstance(value, str) else value
    if _redis_client:
        try:
            await _redis_client.set(key, val_str, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.warning(f"[REDIS] set failed: {e}")
    
    _in_memory_fallback[key] = val_str
    return True

async def get_cache(key: str) -> Optional[Any]:
    """Get key from Redis cache (or in-memory fallback)."""
    if _redis_client:
        try:
            val = await _redis_client.get(key)
            if val:
                try:
                    return json.loads(val)
                except Exception:
                    return val
        except Exception as e:
            logger.warning(f"[REDIS] get failed: {e}")

    val = _in_memory_fallback.get(key)
    if val:
        try:
            return json.loads(val)
        except Exception:
            return val
    return None

async def close_redis() -> None:
    """Close Redis client connection."""
    global _redis_client
    if _redis_client:
        try:
            await _redis_client.close()
            logger.info("[REDIS] Redis connection closed.")
        except Exception:
            pass
        _redis_client = None
