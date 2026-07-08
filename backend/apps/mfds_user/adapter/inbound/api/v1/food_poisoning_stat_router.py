from fastapi import APIRouter, Depends

from mfds_user.adapter.inbound.api.schemas.food_poisoning_stat_schema import (
    FoodStatsByAgentResponse,
    FoodStatsByAgentRow,
    FoodStatsByFacilityResponse,
    FoodStatsByFacilityRow,
    FoodStatsYearlyResponse,
    FoodStatsYearlyRow,
)
from mfds_user.app.ports.input.food_poisoning_stat_use_case import FoodPoisoningStatUseCase
from mfds_user.dependencies.food_poisoning_stat import get_food_poisoning_stat_use_case

router = APIRouter(prefix="/food-stats", tags=["food-stats"])


@router.get("/yearly", response_model=FoodStatsYearlyResponse)
async def food_stats_yearly(
    use_case: FoodPoisoningStatUseCase = Depends(get_food_poisoning_stat_use_case),
) -> FoodStatsYearlyResponse:
    res = await use_case.yearly_stats()
    return FoodStatsYearlyResponse(
        data=[
            FoodStatsYearlyRow(year=r.year, total_incidents=r.total_incidents, total_patients=r.total_patients)
            for r in res.data
        ]
    )


@router.get("/by-agent", response_model=FoodStatsByAgentResponse)
async def food_stats_by_agent(
    year: str | None = None,
    use_case: FoodPoisoningStatUseCase = Depends(get_food_poisoning_stat_use_case),
) -> FoodStatsByAgentResponse:
    res = await use_case.stats_by_agent(year)
    return FoodStatsByAgentResponse(
        year=res.year,
        data=[FoodStatsByAgentRow(agent=r.agent, incidents=r.incidents, patients=r.patients) for r in res.data],
    )


@router.get("/by-facility", response_model=FoodStatsByFacilityResponse)
async def food_stats_by_facility(
    year: str | None = None,
    use_case: FoodPoisoningStatUseCase = Depends(get_food_poisoning_stat_use_case),
) -> FoodStatsByFacilityResponse:
    res = await use_case.stats_by_facility(year)
    return FoodStatsByFacilityResponse(
        year=res.year,
        data=[
            FoodStatsByFacilityRow(facility=r.facility, incidents=r.incidents, patients=r.patients)
            for r in res.data
        ],
    )
