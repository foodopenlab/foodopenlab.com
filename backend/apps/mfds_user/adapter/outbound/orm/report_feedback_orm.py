from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ReportFeedbackORM(Base):
    __tablename__ = "report_feedback"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(ForeignKey("daily_report.id", ondelete="CASCADE"), nullable=False)
    expert_user_id: Mapped[UUID] = mapped_column(ForeignKey("expert_users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    content_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvement_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    usefulness_score: Mapped[int] = mapped_column(SmallInteger, nullable=False)
