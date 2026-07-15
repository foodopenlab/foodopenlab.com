"""Redis 비동기 연결 — apps/ 전역 공유 인프라(rate limit·캐시 등)."""

from __future__ import annotations

import os

from redis.asyncio import Redis

_REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
_client: Redis | None = None


def get_redis() -> Redis:
    """프로세스당 하나의 Redis 클라이언트(문자열 응답)."""
    global _client
    if _client is None:
        _client = Redis.from_url(_REDIS_URL, encoding="utf-8", decode_responses=True)
    return _client
