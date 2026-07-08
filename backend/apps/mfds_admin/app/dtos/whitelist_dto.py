from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional, List

@dataclass(frozen=True)
class AddWhitelistCommand:
    email: str
    invited_name: Optional[str] = None
    role_desc: Optional[str] = None
    added_by: Optional[UUID] = None

@dataclass(frozen=True)
class WhitelistEntryDTO:
    email: str
    invited_name: Optional[str]
    role_desc: Optional[str]
    added_by: UUID
    added_at: datetime
