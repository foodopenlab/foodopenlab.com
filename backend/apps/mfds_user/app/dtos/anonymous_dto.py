from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class AnonymousDTO:
    id: UUID
    cookie_id: str
    created_at: datetime
    last_seen: datetime
