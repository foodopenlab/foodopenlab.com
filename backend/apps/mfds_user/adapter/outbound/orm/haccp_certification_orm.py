"""식품안전나라 HACCP 지정현황 DB 캐시 (I0580/I0610)."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Column, JSON, Text
from sqlmodel import Field, SQLModel


class HaccpCertificationModel(SQLModel, table=True):
    __tablename__: str = "haccp_certifications_cache"

    id: str = Field(primary_key=True, max_length=128)
    service_id: str = Field(nullable=False, max_length=16, index=True)
    business_name: str = Field(nullable=False, max_length=512, index=True)
    normalized_business_name: str = Field(nullable=False, max_length=512, index=True)
    license_number: Optional[str] = Field(default=None, max_length=64, index=True)
    haccp_appn_no: Optional[str] = Field(default=None, max_length=64, index=True)
    designated_date: Optional[str] = Field(default=None, max_length=32)
    expiry_date: Optional[str] = Field(default=None, max_length=32)
    cancelled_date: Optional[str] = Field(default=None, max_length=32)
    returned_date: Optional[str] = Field(default=None, max_length=32)
    product_name: Optional[str] = Field(default=None, max_length=512)
    industry_name: Optional[str] = Field(default=None, max_length=255)
    representative_name: Optional[str] = Field(default=None, max_length=255)
    address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    business_status: Optional[str] = Field(default=None, max_length=64)
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False, index=True))
    raw_json: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    fetched_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)


__all__ = ["HaccpCertificationModel"]
