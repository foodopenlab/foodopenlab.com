from abc import ABC, abstractmethod


class IRagPort(ABC):
    """Driven Port — 사내 도메인 지식(RAG)으로 답변을 생성한다."""

    @abstractmethod
    async def answer(self, question: str, entities: list[str]) -> str: ...
