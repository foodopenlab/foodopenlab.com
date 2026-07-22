from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_dto import Intent


class IIntentClassifierPort(ABC):
    """Driven Port — 질문의 의도를 분류해 목적지·핵심어를 반환한다."""

    @abstractmethod
    async def classify(self, question: str) -> Intent: ...
