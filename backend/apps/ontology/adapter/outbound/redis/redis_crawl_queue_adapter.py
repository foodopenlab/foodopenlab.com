from __future__ import annotations

from matrix.grid_redis_manager import get_redis
from ontology.adapter.outbound.redis import redis_keys
from ontology.app.ports.output.crawl_queue_port import ICrawlQueuePort


class RedisCrawlQueueAdapter(ICrawlQueuePort):
    """크롤러 → 스크래퍼 URL 작업 큐를 Redis LIST로 구현한다."""

    async def enqueue(self, urls: list[str]) -> int:
        if not urls:
            return 0
        await get_redis().rpush(redis_keys.SCRAPER_QUEUE, *urls)
        return len(urls)

    async def dequeue(self) -> str | None:
        return await get_redis().lpop(redis_keys.SCRAPER_QUEUE)
