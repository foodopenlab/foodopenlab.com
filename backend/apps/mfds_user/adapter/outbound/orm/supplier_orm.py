"""납품사 메타데이터(suppliers) 테이블 ORM."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SupplierModel(SQLModel, table=True):
    """납품업체 관리 및 리스크 카드를 위한 도메인 테이블."""

    __tablename__: str = "suppliers"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"name": "id"},
    )
    supplier_name: str = Field(index=True, max_length=255)
    business_no: str = Field(unique=True, index=True, max_length=64)
    representative_name: Optional[str] = Field(default=None, max_length=255)
    supplier_type: Optional[str] = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=datetime.utcnow)


__all__ = ["SupplierModel"]
