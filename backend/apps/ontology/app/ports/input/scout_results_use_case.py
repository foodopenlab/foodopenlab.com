from abc import ABC, abstractmethod

from ontology.app.dtos.scout_dto import ScoutResultsView


class IScoutResultsUseCase(ABC):
    """Driving Port — resources에 저장된 크롤/스크랩 결과를 조회한다."""

    @abstractmethod
    async def list(self, kind: str, limit: int) -> ScoutResultsView: ...
