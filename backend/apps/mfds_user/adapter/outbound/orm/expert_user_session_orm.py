from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ExpertUserSessionORM(Base):
    __tablename__ = "expert_user_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    expert_user_id: Mapped[UUID] = mapped_column(ForeignKey("expert_users.id", ondelete="CASCADE"), nullable=False)
    access_token: Mapped[str] = mapped_column(String(500), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
