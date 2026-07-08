from abc import ABC, abstractmethod
from typing import List, Optional
from mfds_admin.adapter.outbound.orm.expert_whitelist_orm import ExpertWhitelistORM

class WhitelistRepositoryPort(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[ExpertWhitelistORM]:
        pass

    @abstractmethod
    async def save(self, entry: ExpertWhitelistORM) -> ExpertWhitelistORM:
        pass

    @abstractmethod
    async def list_all(self) -> List[ExpertWhitelistORM]:
        pass

    @abstractmethod
    async def delete_by_email(self, email: str) -> bool:
        pass
