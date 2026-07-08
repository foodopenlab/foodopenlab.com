from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ReportFeedbackSectionORM(Base):
    __tablename__ = "report_feedback_sections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    feedback_id: Mapped[UUID] = mapped_column(ForeignKey("report_feedback.id", ondelete="CASCADE"), nullable=False)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'NEWS' | 'RECALL' | ...
