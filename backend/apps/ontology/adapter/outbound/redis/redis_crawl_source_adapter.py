from __future__ import annotations

from matrix.grid_redis_manager import get_redis
from ontology.adapter.outbound.redis import redis_keys
from ontology.app.ports.output.crawl_source_port import ICrawlSourcePort


class RedisCrawlSourceAdapter(ICrawlSourcePort):
    """시드 웹사이트(LIST)와 키워드(SET)를 Redis에서 읽는다."""

    async def next_seed(self) -> str | None:
        return await get_redis().lpop(redis_keys.CRAWLER_TARGETS)

    async def load_keywords(self) -> list[str]:
        return sorted(await get_redis().smembers(redis_keys.CRAWLER_KEYWORDS))
