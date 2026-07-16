from abc import ABC, abstractmethod


class ICrawlQueuePort(ABC):
    """Driven Port — 크롤러 → 스크래퍼로 넘기는 URL 작업 큐(Redis)."""

    @abstractmethod
    async def enqueue(self, urls: list[str]) -> int:
        """URL들을 큐에 넣고, 실제로 넣은 개수를 반환한다."""
        ...

    @abstractmethod
    async def dequeue(self) -> str | None:
        """큐에서 URL 하나를 꺼낸다(없으면 None)."""
        ...
