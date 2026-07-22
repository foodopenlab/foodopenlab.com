from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from matrix.grid_oracle_database_manager import Base


class SemanticAuditLogORM(Base):
    """`semantic_audit_logs` — 시맨틱 게이트웨이 감사 로그."""

    __tablename__ = "semantic_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    client_ip: Mapped[str | None] = mapped_column(String, nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    entities: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    answer_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
