from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from mfds_admin.adapter.outbound.orm.admin_orm import AdminORM

class AdminRepositoryPort(ABC):
    @abstractmethod
    async def get_admin_by_email(self, email: str) -> Optional[AdminORM]:
        pass

    @abstractmethod
    async def update_last_login(self, admin_id: UUID) -> None:
        pass
