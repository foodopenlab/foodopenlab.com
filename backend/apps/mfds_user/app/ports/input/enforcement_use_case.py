from abc import ABC, abstractmethod
from mfds_user.app.dtos.enforcement_dto import (
    EnforcementListQuery,
    EnforcementListDTO,
    EnforcementDTO,
    LatestSanctionsDTO,
)

class EnforcementUseCase(ABC):
    @abstractmethod
    async def list_enforcements(self, query: EnforcementListQuery) -> EnforcementListDTO:
        pass

    @abstractmethod
    async def get_enforcement_detail(self, enforcement_id: str) -> EnforcementDTO:
        pass

    @abstractmethod
    async def latest_sanctions(self) -> LatestSanctionsDTO:
        pass
