"""테스트용 최소 인메모리 async Redis 대역 (decode_responses=True 시맨틱).

RedisRefreshSession이 쓰는 명령만 구현한다: hset/hgetall/expire/sadd/srem/smembers/delete/set/exists.
"""

from __future__ import annotations


class FakeRedis:
    def __init__(self) -> None:
        self._hash: dict[str, dict[str, str]] = {}
        self._set: dict[str, set[str]] = {}
        self._str: dict[str, str] = {}

    async def hset(self, name, key=None, value=None, mapping=None):
        bucket = self._hash.setdefault(name, {})
        if mapping:
            bucket.update({str(k): str(v) for k, v in mapping.items()})
        if key is not None:
            bucket[str(key)] = str(value)
        return 1

    async def hgetall(self, name):
        return dict(self._hash.get(name, {}))

    async def sadd(self, name, *values):
        bucket = self._set.setdefault(name, set())
        bucket.update(str(v) for v in values)
        return len(values)

    async def srem(self, name, *values):
        bucket = self._set.get(name, set())
        for v in values:
            bucket.discard(str(v))
        return len(values)

    async def smembers(self, name):
        return set(self._set.get(name, set()))

    async def delete(self, *names):
        removed = 0
        for name in names:
            for store in (self._hash, self._set, self._str):
                if name in store:
                    del store[name]
                    removed += 1
        return removed

    async def set(self, name, value, ex=None):
        self._str[name] = str(value)
        return True

    async def get(self, name):
        return self._str.get(name)

    async def exists(self, *names):
        return sum(
            1 for n in names if n in self._hash or n in self._set or n in self._str
        )

    async def expire(self, name, seconds):
        return True
