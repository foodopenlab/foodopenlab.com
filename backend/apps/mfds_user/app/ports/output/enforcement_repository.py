from abc import ABC, abstractmethod
from typing import Optional, List
from mfds_user.app.dtos.enforcement_dto import EnforcementDTO

class EnforcementRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, enforcement_id: str) -> Optional[EnforcementDTO]:
        pass

    @abstractmethod
    async def count_all(self) -> int:
        pass

    @abstractmethod
    async def count_list(self, process_type: Optional[str] = None, business_name: Optional[str] = None) -> int:
        pass

    @abstractmethod
    async def get_list(
        self,
        process_type: Optional[str] = None,
        business_name: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> List[EnforcementDTO]:
        pass
