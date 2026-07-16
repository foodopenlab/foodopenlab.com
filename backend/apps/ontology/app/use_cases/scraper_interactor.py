from __future__ import annotations

import logging

from ontology.app.dtos.scrape_dto import ScrapedItem, ScrapeReport, ScrapeRequest
from ontology.app.ports.input.scraper_use_case import IScraperUseCase
from ontology.app.ports.output.crawl_queue_port import ICrawlQueuePort
from ontology.app.ports.output.crawl_source_port import ICrawlSourcePort
from ontology.app.ports.output.scrape_sink_port import IScrapeSinkPort
from ontology.app.ports.output.web_fetcher_port import IWebFetcherPort
from ontology.domain.value_objects.web.keyword_matcher import KeywordSet

logger = logging.getLogger(__name__)

_SNIPPET_RADIUS = 120  # 매칭 키워드 앞뒤로 잘라낼 문자 수


class ScraperInteractor(IScraperUseCase):
    """크롤러가 적재한 URL 큐를 소비해 페이지를 스크랩하는 스크래퍼.

    각 페이지에서 키워드 매칭·스니펫을 추출해 정제 전(raw) 결과로 저장한다.
    """

    def __init__(
        self,
        queue: ICrawlQueuePort,
        fetcher: IWebFetcherPort,
        sink: IScrapeSinkPort,
        source: ICrawlSourcePort,
    ) -> None:
        self._queue = queue
        self._fetcher = fetcher
        self._sink = sink
        self._source = source

    async def scrape(self, request: ScrapeRequest) -> ScrapeReport:
        if request.url:
            await self._queue.enqueue([request.url])

        raw_keywords = (
            request.keywords if request.keywords is not None else await self._source.load_keywords()
        )
        keywords = KeywordSet.of(raw_keywords)

        processed = 0
        scraped = 0
        while processed < request.max_items:
            url = await self._queue.dequeue()
            if url is None:
                break
            processed += 1

            page = await self._fetcher.fetch(url)
            if not page.ok:
                logger.warning(
                    "[ScraperInteractor] 페치 실패 url=%s status=%d",
                    url,
                    page.status_code,
                )
                continue

            haystack = f"{page.title} {page.text}"
            matched = keywords.matches(haystack)
            if not keywords.is_empty and not matched:
                continue

            await self._sink.save(
                ScrapedItem(
                    url=url,
                    title=page.title,
                    matched_keywords=matched,
                    snippet=_snippet(page.text, matched),
                    content=page.text,
                    content_length=len(page.text),
                )
            )
            scraped += 1

        logger.info("[ScraperInteractor] processed=%d scraped=%d", processed, scraped)
        return ScrapeReport(urls_processed=processed, items_scraped=scraped)


def _snippet(text: str, matched: list[str]) -> str:
    """첫 매칭 키워드 주변 텍스트를 잘라 미리보기 스니펫을 만든다."""
    if not matched:
        return text[: _SNIPPET_RADIUS * 2].strip()
    idx = text.lower().find(matched[0].lower())
    if idx < 0:
        return text[: _SNIPPET_RADIUS * 2].strip()
    start = max(0, idx - _SNIPPET_RADIUS)
    end = min(len(text), idx + len(matched[0]) + _SNIPPET_RADIUS)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"
