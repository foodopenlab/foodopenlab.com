from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_dto import SemanticQuery, SemanticResult


class ISemanticUseCase(ABC):
    """Driving Port — 시맨틱 게이트웨이의 단일 진입점."""

    @abstractmethod
    async def ask(self, query: SemanticQuery) -> SemanticResult: ...
