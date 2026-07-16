from abc import ABC, abstractmethod


class ICrawlSourcePort(ABC):
    """Driven Port — 크롤 대상(시드 웹사이트)과 키워드의 공급원(Redis)."""

    @abstractmethod
    async def next_seed(self) -> str | None:
        """대기 중인 시드 URL 하나를 꺼낸다(없으면 None)."""
        ...

    @abstractmethod
    async def load_keywords(self) -> list[str]:
        """크롤러·스크래퍼가 공유하는 키워드 목록을 반환한다."""
        ...
