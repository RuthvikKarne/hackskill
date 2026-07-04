"""Redis connection management.

This module initializes the Redis client for caching, rate limiting, and 
other fast-access operations.
"""
from __future__ import annotations

import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()

# Initialize the Redis connection pool
redis_client = redis.from_url(
    str(settings.REDIS_URL),
    encoding="utf8",
    decode_responses=True,
    max_connections=10,
)

async def get_redis() -> redis.Redis:
    """Dependency to get the Redis client.
    
    Returns:
        The async Redis client instance.
    """
    return redis_client
