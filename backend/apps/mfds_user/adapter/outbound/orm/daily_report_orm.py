from uuid import UUID, uuid4
from datetime import datetime, date
from sqlalchemy import ForeignKey, DateTime, Date, Boolean, Text, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class DailyReportORM(Base):
    __tablename__ = "daily_report"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    expert_user_id: Mapped[UUID] = mapped_column(ForeignKey("expert_users.id", ondelete="CASCADE"), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    summary_preview: Mapped[str] = mapped_column(String(150), default="", nullable=False)

    raw_news: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_recalls: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_laws: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_mfds: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_research: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_stats: Mapped[list | dict] = mapped_column(JSONB, default=list, nullable=False)
    raw_risk: Mapped[list | dict] = mapped_column(JSONB, default=dict, nullable=False)
