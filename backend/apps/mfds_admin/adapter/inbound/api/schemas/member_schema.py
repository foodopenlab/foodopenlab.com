from datetime import datetime

from pydantic import BaseModel


class MemberResponse(BaseModel):
    id: str
    email: str
    name: str | None
    auth_provider: str
    is_expert: bool
    last_login: datetime | None
    created_at: datetime
