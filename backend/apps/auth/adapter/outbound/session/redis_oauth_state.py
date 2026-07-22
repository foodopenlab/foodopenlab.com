"""OAuth state(CSRF) 임시 저장 — Redis, 1회성 소비."""

from __future__ import annotations

from auth.app.ports.output.oauth_state_port import IOAuthStatePort

_STATE_TTL = 600  # 10분


def _state_key(state: str) -> str:
    return f"authz:oauth:state:{state}"


class RedisOAuthState(IOAuthStatePort):
    def __init__(self, redis) -> None:
        self._redis = redis

    async def save_state(self, state: str, provider: str) -> None:
        await self._redis.set(_state_key(state), provider, ex=_STATE_TTL)

    async def consume_state(self, state: str) -> str | None:
        key = _state_key(state)
        provider = await self._redis.get(key)
        if provider is None:
            return None
        await self._redis.delete(key)
        return provider
