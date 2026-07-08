from typing import List

from pydantic import BaseModel, Field


class FoodStatsYearlyRow(BaseModel):
    year: str
    total_incidents: int
    total_patients: int


class FoodStatsYearlyResponse(BaseModel):
    data: List[FoodStatsYearlyRow] = Field(default_factory=list)


class FoodStatsByAgentRow(BaseModel):
    agent: str
    incidents: int
    patients: int


class FoodStatsByAgentResponse(BaseModel):
    year: str
    data: List[FoodStatsByAgentRow] = Field(default_factory=list)


class FoodStatsByFacilityRow(BaseModel):
    facility: str
    incidents: int
    patients: int


class FoodStatsByFacilityResponse(BaseModel):
    year: str
    data: List[FoodStatsByFacilityRow] = Field(default_factory=list)
