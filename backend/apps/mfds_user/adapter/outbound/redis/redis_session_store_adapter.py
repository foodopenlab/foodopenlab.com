from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

from matrix.grid_redis_manager import get_redis
from mfds_user.adapter.outbound.redis import redis_keys
from mfds_user.app.dtos.auth_dto import UserSessionDTO
from mfds_user.app.ports.output.session_store_port import SessionStorePort

logger = logging.getLogger(__name__)

# refresh 토큰 수명(일). access(JWT) 수명은 USER_JWT_EXPIRE_MINUTES를 따른다.
_REFRESH_TTL_DAYS = int(os.getenv("USER_REFRESH_EXPIRE_DAYS", "14"))
_STATE_TTL_SECONDS = 600  # OAuth state 10분


class RedisSessionStoreAdapter(SessionStorePort):
    """발급된 JWT 세션을 Redis에 TTL과 함께 저장한다."""

    def _serialize(self, session: UserSessionDTO) -> str:
        return json.dumps(
            {
                "user_id": str(session.user_id),
                "email": session.email,
                "name": session.name,
                "role": session.role,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at.isoformat(),
            },
            ensure_ascii=False,
        )

    def _deserialize(self, raw: str) -> UserSessionDTO:
        data = json.loads(raw)
        return UserSessionDTO(
            user_id=UUID(data["user_id"]),
            email=data["email"],
            name=data["name"],
            role=data["role"],
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )

    async def save(self, session: UserSessionDTO) -> None:
        redis = get_redis()
        payload = self._serialize(session)
        access_ttl = max(int((session.expires_at - datetime.utcnow()).total_seconds()), 60)
        refresh_ttl = _REFRESH_TTL_DAYS * 24 * 3600

        await redis.set(
            redis_keys.SESSION_BY_ACCESS.format(access_token=session.access_token),
            payload,
            ex=access_ttl,
        )
        await redis.set(
            redis_keys.SESSION_BY_REFRESH.format(refresh_token=session.refresh_token),
            payload,
            ex=refresh_ttl,
        )
        user_key = redis_keys.USER_SESSIONS.format(user_id=session.user_id)
        await redis.sadd(user_key, session.refresh_token)
        await redis.expire(user_key, refresh_ttl)
        logger.info("[RedisSessionStore] saved session user=%s", session.user_id)

    async def find_by_refresh_token(self, refresh_token: str) -> Optional[UserSessionDTO]:
        redis = get_redis()
        raw = await redis.get(redis_keys.SESSION_BY_REFRESH.format(refresh_token=refresh_token))
        return self._deserialize(raw) if raw else None

    async def delete_by_access_token(self, access_token: str) -> None:
        redis = get_redis()
        access_key = redis_keys.SESSION_BY_ACCESS.format(access_token=access_token)
        raw = await redis.get(access_key)
        await redis.delete(access_key)
        if raw:
            data = json.loads(raw)
            await redis.delete(redis_keys.SESSION_BY_REFRESH.format(refresh_token=data["refresh_token"]))
            await redis.srem(redis_keys.USER_SESSIONS.format(user_id=data["user_id"]), data["refresh_token"])

    async def save_state(self, state: str, provider: str) -> None:
        redis = get_redis()
        await redis.set(redis_keys.OAUTH_STATE.format(state=state), provider, ex=_STATE_TTL_SECONDS)

    async def consume_state(self, state: str) -> Optional[str]:
        redis = get_redis()
        key = redis_keys.OAUTH_STATE.format(state=state)
        provider = await redis.get(key)
        if provider is not None:
            await redis.delete(key)
        return provider
