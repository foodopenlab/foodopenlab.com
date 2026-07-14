from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from matrix.grid_embedding_manager import EMBEDDING_DIM
from matrix.grid_oracle_database_manager import Base


class StadiumORM(Base):
    __tablename__ = "stadium"

    stadium_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    # ERD 원본 오타(statdium_name)를 그대로 유지한다.
    statdium_name: Mapped[str] = mapped_column(String(40), nullable=False)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)
    # 구장 편의시설·구조적 특징 시맨틱 검색용 (bge-m3, 1024차원)
    stadium_embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
