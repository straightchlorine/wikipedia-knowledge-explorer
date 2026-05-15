"""Summary cache abstraction over redis.asyncio.

When `redis` is None (no `REDIS_URL` configured) the cache is a no-op: get
returns None and set is silently skipped. This lets the API run in local-dev
or degraded mode without Redis without any branching in the caller.
"""

from __future__ import annotations

import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

CACHE_KEY_PREFIX = "wke:summary:"


class SummaryCache:
    def __init__(self, redis: Redis | None, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl_seconds = ttl_seconds

    async def get(self, key: str) -> str | None:
        if self._redis is None:
            return None
        try:
            value = await self._redis.get(key)
        except RedisError as exc:
            logger.warning("redis GET failed; treating as miss: %s", exc.__class__.__name__)
            return None
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    async def set(self, key: str, value: str) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.set(key, value, ex=self._ttl_seconds)
        except RedisError as exc:
            logger.warning("redis SET failed; cache write skipped: %s", exc.__class__.__name__)

    async def close(self) -> None:
        if self._redis is None:
            return
        await self._redis.aclose()
