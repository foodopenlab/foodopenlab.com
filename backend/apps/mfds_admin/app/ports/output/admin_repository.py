from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from mfds_admin.domain.entities.admin_entity import Admin

class AdminRepositoryPort(ABC):
    @abstractmethod
    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        pass

    @abstractmethod
    async def update_last_login(self, admin_id: UUID) -> None:
        pass

    @abstractmethod
    async def upsert_google_admin(self, email: str, name: str) -> Admin:
        """구글 로그인 어드민을 email 기준으로 조회/생성하고 last_login을 갱신한다."""
        pass
