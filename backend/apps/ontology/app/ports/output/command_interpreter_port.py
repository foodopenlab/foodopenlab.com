from abc import ABC, abstractmethod

from ontology.app.dtos.scout_dto import ScoutPlan


class ICommandInterpreterPort(ABC):
    """Driven Port — 자연어 수집 명령을 실행 계획(ScoutPlan)으로 해석한다."""

    @abstractmethod
    async def interpret(self, mode: str, command: str) -> ScoutPlan: ...
