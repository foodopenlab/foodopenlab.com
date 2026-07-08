"""식품안전나라 행정처분 API 캐시 테이블 `enforcement_cache`."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, SQLModel


class EnforcementModel(SQLModel, table=True):
    __tablename__: str = "enforcement_cache"

    id: str = Field(primary_key=True, max_length=64)
    business_name: str = Field(nullable=False, max_length=512)
    business_type: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    process_type: Optional[str] = Field(default=None, max_length=64)
    violation_content: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    violation_date: Optional[str] = Field(default=None, max_length=32)
    process_date: Optional[str] = Field(default=None, max_length=32)
    district: Optional[str] = Field(default=None, max_length=255)
    raw_json: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    fetched_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["EnforcementModel"]
