from abc import ABC, abstractmethod

from ontology.app.dtos.scrape_dto import ScrapedItem


class IScrapeSinkPort(ABC):
    """Driven Port — 스크랩 결과의 저장소(resources 파일)."""

    @abstractmethod
    async def save(self, item: ScrapedItem) -> None: ...
