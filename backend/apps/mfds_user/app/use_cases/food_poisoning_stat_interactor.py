from typing import Optional

from mfds_user.app.dtos.food_poisoning_stat_dto import AgentStatDTO, FacilityStatDTO, YearlyStatDTO
from mfds_user.app.ports.input.food_poisoning_stat_use_case import FoodPoisoningStatUseCase
from mfds_user.app.ports.output.food_poisoning_stat_repository import (
    FoodPoisoningStatRepositoryPort,
)


class FoodPoisoningStatInteractor(FoodPoisoningStatUseCase):
    def __init__(self, repository: FoodPoisoningStatRepositoryPort) -> None:
        self._repo = repository

    async def yearly_stats(self) -> YearlyStatDTO:
        rows = await self._repo.get_yearly()
        return YearlyStatDTO(data=rows)

    async def stats_by_agent(self, year: Optional[str]) -> AgentStatDTO:
        rows = await self._repo.get_by_agent(year)
        return AgentStatDTO(year=year or "전체", data=rows)

    async def stats_by_facility(self, year: Optional[str]) -> FacilityStatDTO:
        rows = await self._repo.get_by_facility(year)
        return FacilityStatDTO(year=year or "전체", data=rows)
