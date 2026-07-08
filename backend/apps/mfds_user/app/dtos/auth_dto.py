from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class SignupCommand:
    email: str
    password: str
    name: str
    agreed: bool
    role: str

@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str

@dataclass(frozen=True)
class UserSessionDTO:
    user_id: UUID
    email: str
    name: str
    role: str
    access_token: str
    refresh_token: str
    expires_at: datetime
