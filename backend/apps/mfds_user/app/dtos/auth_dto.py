from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class UserSessionDTO:
    user_id: UUID
    email: str
    name: str
    role: str
    access_token: str
    refresh_token: str
    expires_at: datetime
