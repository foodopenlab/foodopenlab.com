from typing import Any, List, Optional, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.adapter.outbound.orm.food_poisoning_stat_orm import FoodPoisoningStatModel
from mfds_user.app.dtos.food_poisoning_stat_dto import (
    AgentStatRowDTO,
    FacilityStatRowDTO,
    YearlyStatRowDTO,
)
from mfds_user.app.ports.output.food_poisoning_stat_repository import (
    FoodPoisoningStatRepositoryPort,
)


class FoodPoisoningStatPgRepository(FoodPoisoningStatRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_all(self) -> int:
        res = await self.session.execute(select(func.count()).select_from(FoodPoisoningStatModel))
        return int(res.scalar_one())

    async def get_yearly(self) -> List[YearlyStatRowDTO]:
        M = FoodPoisoningStatModel
        stmt = (
            select(M.occurrence_year, func.sum(M.incident_count), func.sum(M.patient_count))
            .where(cast(Any, M.category) == "agent")
            .group_by(M.occurrence_year)
            .order_by(M.occurrence_year)
        )
        res = await self.session.execute(stmt)
        return [
            YearlyStatRowDTO(year=year, total_incidents=int(incidents or 0), total_patients=int(patients or 0))
            for year, incidents, patients in res.all()
        ]

    async def get_by_agent(self, year: Optional[str] = None) -> List[AgentStatRowDTO]:
        M = FoodPoisoningStatModel
        stmt = select(M.label, func.sum(M.incident_count), func.sum(M.patient_count)).where(
            cast(Any, M.category) == "agent"
        )
        if year:
            stmt = stmt.where(cast(Any, M.occurrence_year) == year)
        stmt = stmt.group_by(M.label).order_by(func.sum(M.incident_count).desc())
        res = await self.session.execute(stmt)
        return [
            AgentStatRowDTO(agent=label, incidents=int(incidents or 0), patients=int(patients or 0))
            for label, incidents, patients in res.all()
        ]

    async def get_by_facility(self, year: Optional[str] = None) -> List[FacilityStatRowDTO]:
        M = FoodPoisoningStatModel
        stmt = select(M.label, func.sum(M.incident_count), func.sum(M.patient_count)).where(
            cast(Any, M.category) == "facility"
        )
        if year:
            stmt = stmt.where(cast(Any, M.occurrence_year) == year)
        stmt = stmt.group_by(M.label).order_by(func.sum(M.incident_count).desc())
        res = await self.session.execute(stmt)
        return [
            FacilityStatRowDTO(facility=label, incidents=int(incidents or 0), patients=int(patients or 0))
            for label, incidents, patients in res.all()
        ]
