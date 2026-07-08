"""식품안전나라 식중독 통계(I2850 원인물질별/I2849 원인시설별) 캐시 테이블."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, Integer, JSON
from sqlmodel import Field, SQLModel


class FoodPoisoningStatModel(SQLModel, table=True):
    __tablename__: str = "food_poisoning_stat_cache"

    id: str = Field(primary_key=True, max_length=64)
    category: str = Field(nullable=False, max_length=16)
    label: str = Field(nullable=False, max_length=255)
    occurrence_year: str = Field(nullable=False, max_length=8)
    occurrence_month: Optional[str] = Field(default=None, max_length=8)
    incident_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    patient_count: int = Field(default=0, sa_column=Column(Integer, nullable=False))
    raw_json: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    fetched_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["FoodPoisoningStatModel"]
