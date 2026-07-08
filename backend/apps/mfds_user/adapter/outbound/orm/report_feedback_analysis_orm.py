from uuid import UUID, uuid4
from datetime import datetime, date
from sqlalchemy import DateTime, Date, Integer, Text, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ReportFeedbackAnalysisORM(Base):
    __tablename__ = "report_feedback_analysis"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    industry_code: Mapped[str] = mapped_column(String(255), nullable=False)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    feedback_count: Mapped[int] = mapped_column(Integer, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    missing_topics: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    improvement_keys: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    useful_sections: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    action_items: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
