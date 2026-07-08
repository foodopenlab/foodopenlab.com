from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from mfds_user.domain.value_objects.user_role_vo import UserRole

@dataclass
class User:
    id: UUID
    email: str
    name: str | None
    picture: str | None
    role: UserRole
    created_at: datetime
    last_login: datetime | None

    def is_expert_or_above(self) -> bool:
        return self.role in [UserRole.EXPERT, UserRole.ADMIN]

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
