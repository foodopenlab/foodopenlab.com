from abc import ABC, abstractmethod

from ontology.app.dtos.scout_dto import ScoutPlan


class IScoutRequestSinkPort(ABC):
    """Driven Port — 어드민이 입력한 스카우트 요청(URL·명령·해석계획)을 이력으로 기록한다(Redis)."""

    @abstractmethod
    async def record(self, mode: str, url: str, command: str, plan: ScoutPlan) -> None: ...
