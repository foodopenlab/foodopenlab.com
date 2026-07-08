"""SmithCaptain — 페르소나 스텁 + 채팅 메시지 ORM."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from matrix.grid_neo_theone_base import Base as PersonaBase
from matrix.grid_oracle_database_manager import Base


class SmithCaptainOrm(PersonaBase):
    __abstract__ = True

