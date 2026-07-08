from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ExpertFeedbackORM(Base):
    __tablename__ = "expert_feedbacks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    message_id: Mapped[UUID] = mapped_column(nullable=False)
    expert_user_id: Mapped[UUID] = mapped_column(ForeignKey("expert_users.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(20), nullable=False)  # 'correct' | 'partial' | 'incorrect'
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
