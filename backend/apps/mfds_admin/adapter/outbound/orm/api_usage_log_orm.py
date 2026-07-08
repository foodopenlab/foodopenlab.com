from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class ApiUsageLogORM(Base):
    __tablename__ = "api_usage_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'expert' | 'anonymous'
    actor_id: Mapped[UUID] = mapped_column(nullable=False)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)  # '식품안전나라' | '법제처' | 'Gemini'
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
