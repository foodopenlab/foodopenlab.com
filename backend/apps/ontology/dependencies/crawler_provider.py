from fastapi import Depends

from ontology.adapter.outbound.files.file_crawl_sink_adapter import FileCrawlSinkAdapter
from ontology.adapter.outbound.redis.redis_crawl_queue_adapter import (
    RedisCrawlQueueAdapter,
)
from ontology.adapter.outbound.redis.redis_crawl_source_adapter import (
    RedisCrawlSourceAdapter,
)
from ontology.adapter.outbound.web.httpx_web_fetcher_adapter import (
    HttpxWebFetcherAdapter,
)
from ontology.app.ports.input.crawler_use_case import ICrawlerUseCase
from ontology.app.ports.output.crawl_queue_port import ICrawlQueuePort
from ontology.app.ports.output.crawl_sink_port import ICrawlSinkPort
from ontology.app.ports.output.crawl_source_port import ICrawlSourcePort
from ontology.app.ports.output.web_fetcher_port import IWebFetcherPort
from ontology.app.use_cases.crawler_interactor import CrawlerInteractor


def get_crawl_source() -> ICrawlSourcePort:
    return RedisCrawlSourceAdapter()


def get_web_fetcher() -> IWebFetcherPort:
    return HttpxWebFetcherAdapter()


def get_crawl_queue() -> ICrawlQueuePort:
    return RedisCrawlQueueAdapter()


def get_crawl_sink() -> ICrawlSinkPort:
    return FileCrawlSinkAdapter()


def get_crawler_use_case(
    source: ICrawlSourcePort = Depends(get_crawl_source),
    fetcher: IWebFetcherPort = Depends(get_web_fetcher),
    queue: ICrawlQueuePort = Depends(get_crawl_queue),
    sink: ICrawlSinkPort = Depends(get_crawl_sink),
) -> ICrawlerUseCase:
    return CrawlerInteractor(source=source, fetcher=fetcher, queue=queue, sink=sink)
