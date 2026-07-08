from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class AdminLoginCommand:
    email: str
    password: str

@dataclass(frozen=True)
class AdminTokenDTO:
    access_token: str
    token_type: str
    expires_in: int
    admin_name: str
    admin_id: UUID
