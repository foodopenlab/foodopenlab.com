from abc import ABC, abstractmethod


class IScoutResultReaderPort(ABC):
    """Driven Port — resources에 저장된 크롤/스크랩 결과(JSONL)를 읽어온다."""

    @abstractmethod
    async def read(self, kind: str, limit: int) -> list[dict]:
        """kind('crawled'|'scraped')의 결과를 최신순으로 최대 limit개 반환한다."""
        ...
