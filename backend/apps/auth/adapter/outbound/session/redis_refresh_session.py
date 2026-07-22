"""Redis 기반 refresh 세션 — 로테이션 + 재사용 감지 + jti 블랙리스트.

토큰 원문은 저장하지 않고 SHA-256 해시만 저장한다.
재사용(이미 로테이션된 토큰 재제시) 감지 시 해당 sub의 **모든 세션을 폐기**한다.

Redis 키(doc §5):
- `authz:refresh:{token_hash}`      → hash{status, sub}  (TTL=refresh 수명)
- `authz:user:{sub}:tokens`          → set(token_hash…)   (sub 전체 폐기용)
- `authz:jti:block:{jti}`            → "1"                 (즉시차단, TTL=access 잔여수명)
"""

from __future__ import annotations

import hashlib
import os
import secrets

from auth.app.dtos.auth_dto import RefreshRotation
from auth.app.ports.output.refresh_session_port import IRefreshSessionPort
from auth.domain.exceptions import InvalidRefreshError, RefreshReuseError

_DEFAULT_REFRESH_TTL = 60 * 60 * 24 * 14  # 14일


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _refresh_key(token_hash: str) -> str:
    return f"authz:refresh:{token_hash}"


def _user_key(sub: str) -> str:
    return f"authz:user:{sub}:tokens"


def _jti_key(jti: str) -> str:
    return f"authz:jti:block:{jti}"


class RedisRefreshSession(IRefreshSessionPort):
    def __init__(self, redis, ttl_seconds: int | None = None) -> None:
        self._redis = redis
        self._ttl = ttl_seconds or int(os.getenv("AUTH_REFRESH_TTL_SEC", str(_DEFAULT_REFRESH_TTL)))

    async def start(self, sub: str) -> str:
        token = secrets.token_urlsafe(32)
        await self._register(sub, token)
        return token

    async def rotate(self, refresh_token: str) -> RefreshRotation:
        token_hash = _hash(refresh_token)
        key = _refresh_key(token_hash)
        data = await self._redis.hgetall(key)
        if not data:
            raise InvalidRefreshError("유효하지 않거나 만료된 refresh 토큰입니다.")

        sub = data.get("sub", "")
        if data.get("status") == "used":
            # 이미 로테이션된 토큰의 재제시 = 탈취 정황 → sub 세션 전체 폐기
            await self._revoke_all(sub)
            raise RefreshReuseError("refresh 토큰 재사용이 감지되어 모든 세션이 폐기되었습니다.")

        await self._redis.hset(key, "status", "used")
        new_token = secrets.token_urlsafe(32)
        await self._register(sub, new_token)
        return RefreshRotation(sub=sub, refresh_token=new_token)

    async def revoke(self, refresh_token: str) -> None:
        token_hash = _hash(refresh_token)
        data = await self._redis.hgetall(_refresh_key(token_hash))
        if not data:
            return
        sub = data.get("sub")
        await self._redis.delete(_refresh_key(token_hash))
        if sub:
            await self._redis.srem(_user_key(sub), token_hash)

    async def blacklist_jti(self, jti: str, ttl_seconds: int) -> None:
        await self._redis.set(_jti_key(jti), "1", ex=max(1, ttl_seconds))

    async def is_jti_blacklisted(self, jti: str) -> bool:
        return bool(await self._redis.exists(_jti_key(jti)))

    async def _register(self, sub: str, token: str) -> None:
        token_hash = _hash(token)
        key = _refresh_key(token_hash)
        await self._redis.hset(key, mapping={"status": "active", "sub": sub})
        await self._redis.expire(key, self._ttl)
        await self._redis.sadd(_user_key(sub), token_hash)
        await self._redis.expire(_user_key(sub), self._ttl)

    async def _revoke_all(self, sub: str) -> None:
        if not sub:
            return
        hashes = await self._redis.smembers(_user_key(sub))
        keys = [_refresh_key(h) for h in hashes] + [_user_key(sub)]
        if keys:
            await self._redis.delete(*keys)
