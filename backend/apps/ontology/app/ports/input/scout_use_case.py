from abc import ABC, abstractmethod

from ontology.app.dtos.scout_dto import ScoutCommand, ScoutResult


class IScoutUseCase(ABC):
    """Driving Port — URL과 자연어 명령을 받아 해석 후 크롤/스크랩을 실행한다."""

    @abstractmethod
    async def run(self, command: ScoutCommand) -> ScoutResult: ...
