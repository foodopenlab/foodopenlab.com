from abc import ABC, abstractmethod

from ontology.app.dtos.crawl_dto import CrawlReport, CrawlRequest


class ICrawlerUseCase(ABC):
    """Driving Port — 크롤러의 단일 진입점.

    Redis에서 시드 웹사이트·키워드를 읽어 같은 도메인을 탐색하고,
    키워드 관련 URL을 스크래퍼 큐에 적재한다.
    """

    @abstractmethod
    async def crawl(self, request: CrawlRequest) -> CrawlReport: ...
