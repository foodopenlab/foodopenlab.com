from abc import ABC, abstractmethod
from typing import Optional

from mfds_user.app.dtos.food_poisoning_stat_dto import AgentStatDTO, FacilityStatDTO, YearlyStatDTO


class FoodPoisoningStatUseCase(ABC):
    @abstractmethod
    async def yearly_stats(self) -> YearlyStatDTO: ...

    @abstractmethod
    async def stats_by_agent(self, year: Optional[str]) -> AgentStatDTO: ...

    @abstractmethod
    async def stats_by_facility(self, year: Optional[str]) -> FacilityStatDTO: ...
