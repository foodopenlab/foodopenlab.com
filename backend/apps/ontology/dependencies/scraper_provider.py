from fastapi import Depends

from ontology.adapter.outbound.files.file_scrape_sink_adapter import (
    FileScrapeSinkAdapter,
    SplitMode,
)
from ontology.app.ports.input.scraper_use_case import IScraperUseCase
from ontology.app.ports.output.crawl_queue_port import ICrawlQueuePort
from ontology.app.ports.output.crawl_source_port import ICrawlSourcePort
from ontology.app.ports.output.scrape_sink_port import IScrapeSinkPort
from ontology.app.ports.output.web_fetcher_port import IWebFetcherPort
from ontology.app.use_cases.scraper_interactor import ScraperInteractor
from ontology.dependencies.crawler_provider import (
    get_crawl_queue,
    get_crawl_source,
    get_web_fetcher,
)


def get_scrape_sink(split: SplitMode = SplitMode.SINGLE) -> IScrapeSinkPort:
    # split 은 Depends 가 아닌 기본값 파라미터라 FastAPI 가 쿼리 파라미터로 노출한다.
    # 예) POST /api/scraper/run?split=date  → 일자별 scraped-YYYYMMDD.jsonl 로 분리.
    return FileScrapeSinkAdapter(split=split)


def get_scraper_use_case(
    queue: ICrawlQueuePort = Depends(get_crawl_queue),
    fetcher: IWebFetcherPort = Depends(get_web_fetcher),
    sink: IScrapeSinkPort = Depends(get_scrape_sink),
    source: ICrawlSourcePort = Depends(get_crawl_source),
) -> IScraperUseCase:
    return ScraperInteractor(queue=queue, fetcher=fetcher, sink=sink, source=source)
