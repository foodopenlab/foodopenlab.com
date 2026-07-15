from __future__ import annotations

import logging
import os
import time

from fastapi import HTTPException, Request, status

from matrix.grid_redis_manager import get_redis

logger = logging.getLogger(__name__)

# LLM 분류 이전에 실행되는 값싼 게이트 — 서버 과부하·쿼터 소진 공격 방어.
_LIMIT = int(os.getenv("GATEWAY_RATE_LIMIT_PER_MIN", "30"))
_WINDOW_SEC = 60


async def enforce_rate_limit(request: Request) -> None:
    """IP당 분당 요청 수 제한(fixed window). Redis 장애 시 fail-open."""
    client_ip = request.client.host if request.client else "unknown"
    window = int(time.time()) // _WINDOW_SEC
    key = f"gw:rl:{client_ip}:{window}"

    try:
        redis = get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, _WINDOW_SEC)
    except Exception as exc:
        # rate limit 인프라 장애가 서비스를 막아서는 안 된다(가용성 우선).
        logger.warning("[rate_limit] Redis 오류로 fail-open: %s", exc)
        return

    if count > _LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"요청이 너무 많습니다. 분당 {_LIMIT}회로 제한됩니다.",
        )
