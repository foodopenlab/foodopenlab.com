from abc import ABC, abstractmethod

from ontology.app.dtos.scrape_dto import ScrapeReport, ScrapeRequest


class IScraperUseCase(ABC):
    """Driving Port — 스크래퍼의 단일 진입점.

    크롤러가 적재한 URL 큐를 소비해 페이지를 페치하고,
    키워드 매칭 결과를 저장소(resources)에 기록한다.
    """

    @abstractmethod
    async def scrape(self, request: ScrapeRequest) -> ScrapeReport: ...
