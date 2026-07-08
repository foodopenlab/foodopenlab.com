from uuid import UUID
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ExpertWhitelistORM(Base):
    __tablename__ = "expert_whitelist"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    invited_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role_desc: Mapped[str | None] = mapped_column(String(50), nullable=True)
    added_by: Mapped[UUID] = mapped_column(ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
