from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ExpertUserIndustryORM(Base):
    __tablename__ = "expert_user_industry"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    expert_user_id: Mapped[UUID] = mapped_column(ForeignKey("expert_users.id", ondelete="CASCADE"), nullable=False)
    category_code: Mapped[str] = mapped_column(String(255), ForeignKey("industry_category.code", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
