from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class SearchLogORM(Base):
    __tablename__ = "search_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'expert' | 'anonymous'
    actor_id: Mapped[UUID] = mapped_column(nullable=False)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    query_pattern: Mapped[str] = mapped_column(String(50), nullable=False)  # 'law' | 'ingredient' | 'haccp' | 'general'
    searched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
