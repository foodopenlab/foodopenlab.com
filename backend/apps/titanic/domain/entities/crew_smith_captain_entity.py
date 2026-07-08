from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class SmithCaptainChatMessage:
    id: UUID
    session_key: str
    role: str
    content: str
    model: str | None
    created_at: datetime
