"""Semantic caching for AI Engine responses.

Uses Redis to cache AI generation results for identical prompts.
This significantly reduces Gemini API costs, lowers latency, and
prevents duplicate identical requests.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import redis.asyncio as aioredis

# Use a lightweight hash for semantic caching
def _hash_prompt(prompt: str) -> str:
    """Create a deterministic hash for a prompt string."""
    return hashlib.sha256(prompt.strip().lower().encode("utf-8")).hexdigest()

class AICache:
    """Redis-backed cache for AI model responses."""
    
    def __init__(self, redis_url: str):
        self._redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        # Cache for 24 hours by default
        self._ttl = 60 * 60 * 24

    async def get_cached_response(self, prompt: str) -> dict[str, Any] | str | None:
        """Retrieve a cached response if the prompt was seen before."""
        key = f"ai_cache:{_hash_prompt(prompt)}"
        result = await self._redis.get(key)
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return None

    async def set_cached_response(self, prompt: str, response: dict[str, Any] | str, ttl: int | None = None) -> None:
        """Store a successful AI response in the cache."""
        key = f"ai_cache:{_hash_prompt(prompt)}"
        val = json.dumps(response) if isinstance(response, dict) else response
        await self._redis.set(key, val, ex=ttl or self._ttl)

# Global singleton
_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ai_cache = AICache(redis_url=_redis_url)
