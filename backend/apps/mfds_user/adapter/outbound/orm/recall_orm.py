"""식품안전나라 회수제품 API 캐시 테이블 `recalls_cache`."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, Integer, JSON, Text
from sqlmodel import Field, SQLModel


class RecallModel(SQLModel, table=True):
    __tablename__: str = "recalls_cache"

    id: str = Field(primary_key=True, max_length=64)
    product_name: str = Field(nullable=False, max_length=512)
    manufacturer: str = Field(nullable=False, max_length=512)
    food_type: Optional[str] = Field(default=None, max_length=255)
    food_category: Optional[str] = Field(default=None, max_length=255)
    recall_reason: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    recall_grade: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    recall_method: Optional[str] = Field(default=None, max_length=255)
    registered_at: Optional[str] = Field(default=None, max_length=32)
    image_url: Optional[str] = Field(default=None, max_length=2048)
    raw_json: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    fetched_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


__all__ = ["RecallModel"]
