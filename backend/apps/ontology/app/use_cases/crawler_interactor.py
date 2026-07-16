from __future__ import annotations

import logging
from collections import deque
from urllib.parse import urldefrag, urlparse

from ontology.app.dtos.crawl_dto import CrawlReport, CrawlRequest
from ontology.app.ports.input.crawler_use_case import ICrawlerUseCase
from ontology.app.ports.output.crawl_queue_port import ICrawlQueuePort
from ontology.app.ports.output.crawl_source_port import ICrawlSourcePort
from ontology.app.ports.output.web_fetcher_port import IWebFetcherPort
from ontology.domain.value_objects.web.keyword_matcher import KeywordSet

logger = logging.getLogger(__name__)


class CrawlerInteractor(ICrawlerUseCase):
    """Redis 시드에서 시작해 같은 도메인을 너비우선(BFS) 탐색하는 크롤러.

    각 페이지의 텍스트가 키워드와 매칭되면 그 URL을 스크래퍼 큐에 적재한다.
    (키워드가 비어 있으면 방문한 모든 페이지를 관련 페이지로 간주한다.)
    """

    def __init__(
        self,
        source: ICrawlSourcePort,
        fetcher: IWebFetcherPort,
        queue: ICrawlQueuePort,
    ) -> None:
        self._source = source
        self._fetcher = fetcher
        self._queue = queue

    async def crawl(self, request: CrawlRequest) -> CrawlReport:
        seed = request.seed or await self._source.next_seed()
        if seed is None:
            logger.info("[CrawlerInteractor] 대기 중인 시드 없음")
            return CrawlReport(seed=None)

        raw_keywords = (
            request.keywords if request.keywords is not None else await self._source.load_keywords()
        )
        keywords = KeywordSet.of(raw_keywords)
        seed_host = urlparse(seed).netloc

        visited: set[str] = set()
        frontier: deque[tuple[str, int]] = deque([(_normalize(seed), 0)])
        relevant: list[str] = []
        pages_visited = 0

        while frontier and pages_visited < request.max_pages:
            url, depth = frontier.popleft()
            if url in visited:
                continue
            visited.add(url)

            page = await self._fetcher.fetch(url)
            pages_visited += 1
            if not page.ok:
                continue

            if keywords.any_match(f"{page.title} {page.text}"):
                relevant.append(url)

            if depth < request.max_depth:
                for link in page.links:
                    target = _normalize(link)
                    if urlparse(target).netloc == seed_host and target not in visited:
                        frontier.append((target, depth + 1))

        enqueued = await self._queue.enqueue(relevant)
        logger.info(
            "[CrawlerInteractor] seed=%s visited=%d enqueued=%d",
            seed,
            pages_visited,
            enqueued,
        )
        return CrawlReport(
            seed=seed,
            keywords=list(keywords.values),
            pages_visited=pages_visited,
            urls_enqueued=enqueued,
        )


def _normalize(url: str) -> str:
    """프래그먼트(#...)를 제거해 같은 페이지가 중복 방문되지 않게 한다."""
    return urldefrag(url).url
