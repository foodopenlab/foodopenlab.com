from __future__ import annotations

import logging

from ontology.app.dtos.crawl_dto import CrawlRequest
from ontology.app.dtos.scout_dto import ScoutCommand, ScoutPlan, ScoutResult
from ontology.app.dtos.scrape_dto import ScrapeRequest
from ontology.app.ports.input.crawler_use_case import ICrawlerUseCase
from ontology.app.ports.input.scout_use_case import IScoutUseCase
from ontology.app.ports.input.scraper_use_case import IScraperUseCase
from ontology.app.ports.output.command_interpreter_port import ICommandInterpreterPort
from ontology.app.ports.output.scout_request_sink_port import IScoutRequestSinkPort

logger = logging.getLogger(__name__)

_CRAWLER = "crawler"
_SCRAPER = "scraper"


class ScoutInteractor(IScoutUseCase):
    """자연어 명령 해석 → 모드별 수집 실행 오케스트레이터.

    모드 분기는 조건문이 아니라 핸들러 매핑(dispatch table)으로 처리한다.
    """

    def __init__(
        self,
        interpreter: ICommandInterpreterPort,
        crawler: ICrawlerUseCase,
        scraper: IScraperUseCase,
        request_sink: IScoutRequestSinkPort,
    ) -> None:
        self._interpreter = interpreter
        self._crawler = crawler
        self._scraper = scraper
        self._request_sink = request_sink
        self._handlers = {
            _CRAWLER: self._run_crawler,
            _SCRAPER: self._run_scraper,
        }

    async def run(self, command: ScoutCommand) -> ScoutResult:
        handler = self._handlers.get(command.mode)
        if handler is None:
            raise ValueError(f"지원하지 않는 모드입니다: {command.mode}")

        url = command.url.strip()
        if not url:
            raise ValueError("사이트 주소(URL)를 입력해 주세요.")

        plan = await self._interpreter.interpret(command.mode, command.command)
        # 입력(URL·명령)과 해석 계획을 Redis 이력에 남긴다(실행 전에 기록).
        await self._request_sink.record(command.mode, url, command.command, plan)
        summary = await handler(url, plan)
        logger.info("[ScoutInteractor] mode=%s url=%s summary=%s", command.mode, url, summary)
        return ScoutResult(mode=command.mode, plan=plan, summary=summary)

    async def _run_crawler(self, url: str, plan: ScoutPlan) -> dict[str, object]:
        report = await self._crawler.crawl(
            CrawlRequest(
                max_pages=plan.max_pages,
                max_depth=plan.max_depth,
                seed=url,
                keywords=plan.keywords,
                enqueue_to_scraper=False,
            )
        )
        return {
            "seed": report.seed,
            "keywords": report.keywords,
            "pages_visited": report.pages_visited,
            "findings_saved": report.findings_saved,
        }

    async def _run_scraper(self, url: str, plan: ScoutPlan) -> dict[str, object]:
        report = await self._scraper.scrape(
            ScrapeRequest(
                max_items=plan.max_items,
                url=url,
                keywords=plan.keywords,
            )
        )
        return {
            "urls_processed": report.urls_processed,
            "items_scraped": report.items_scraped,
        }
