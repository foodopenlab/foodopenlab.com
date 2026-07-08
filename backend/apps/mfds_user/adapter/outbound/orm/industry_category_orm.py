from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class IndustryCategoryORM(Base):
    __tablename__ = "industry_category"

    code: Mapped[str] = mapped_column(String(255), primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'media' | 'foodtype'
    parent_code: Mapped[str | None] = mapped_column(String(255), ForeignKey("industry_category.code", ondelete="CASCADE"), nullable=True)
    depth: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    is_flat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    name_ko: Mapped[str] = mapped_column(String(255), nullable=False)
    crawler_param: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
