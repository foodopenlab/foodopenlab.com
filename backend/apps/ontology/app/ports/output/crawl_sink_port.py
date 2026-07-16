from abc import ABC, abstractmethod

from ontology.app.dtos.crawl_dto import CrawlFinding


class ICrawlSinkPort(ABC):
    """Driven Port — 크롤러가 찾은 관련 페이지의 저장소(resources 파일)."""

    @abstractmethod
    async def save(self, findings: list[CrawlFinding]) -> None: ...
