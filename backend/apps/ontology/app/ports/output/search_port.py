from abc import ABC, abstractmethod


class ISearchPort(ABC):
    """Driven Port — 단순 데이터 조회(자연어 검색)를 수행한다."""

    @abstractmethod
    async def search(self, question: str, entities: list[str]) -> str: ...
