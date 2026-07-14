from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from matrix.grid_embedding_manager import EMBEDDING_DIM
from matrix.grid_oracle_database_manager import Base


class LawChunkORM(Base):
    """`law_chunks` — krcofoodrm 코퍼스에서 이관한 44,518개 임베딩 청크.

    embedding은 bge-m3(1024차원)로, 프로젝트 `grid_embedding_manager`와 동일 벡터 공간.
    """

    __tablename__ = "law_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str | None] = mapped_column(String, nullable=True)
    law_nm: Mapped[str | None] = mapped_column(String, nullable=True)
    article_no: Mapped[str | None] = mapped_column(String, nullable=True)
    article_title: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    enforce_dt: Mapped[str | None] = mapped_column(String, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    embed_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    last_updt_dt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
