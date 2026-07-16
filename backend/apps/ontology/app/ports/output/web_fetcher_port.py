from abc import ABC, abstractmethod

from ontology.app.dtos.web_dto import FetchedPage


class IWebFetcherPort(ABC):
    """Driven Port — URL을 받아 파싱된 페이지(FetchedPage)를 반환한다."""

    @abstractmethod
    async def fetch(self, url: str) -> FetchedPage:
        """페치 실패 시 예외 대신 status_code=0 인 FetchedPage를 반환한다."""
        ...
