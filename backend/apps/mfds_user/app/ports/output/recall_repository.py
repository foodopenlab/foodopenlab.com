from abc import ABC, abstractmethod
from typing import Optional, List
from mfds_user.app.dtos.recall_dto import RecallDTO

class RecallRepositoryPort(ABC):
    @abstractmethod
    async def get_by_id(self, recall_id: str) -> Optional[RecallDTO]:
        pass

    @abstractmethod
    async def count_all(self) -> int:
        pass

    @abstractmethod
    async def list_distinct_food_types(self) -> List[str]:
        pass

    @abstractmethod
    async def count_list(self, food_category: Optional[str] = None, grade: Optional[int] = None) -> int:
        pass

    @abstractmethod
    async def get_list(
        self,
        food_category: Optional[str] = None,
        grade: Optional[int] = None,
        page: int = 1,
        size: int = 20,
        offset: Optional[int] = None,
    ) -> List[RecallDTO]:
        pass

    @abstractmethod
    async def get_latest_by_category(
        self,
        food_category: str,
        grade: Optional[int] = None,
        limit: int = 5,
    ) -> List[RecallDTO]:
        pass

    @abstractmethod
    async def get_latest_by_food_type(
        self,
        keyword: str,
        grade: Optional[int] = None,
        limit: int = 5,
    ) -> List[RecallDTO]:
        pass

    @abstractmethod
    async def count_by_manufacturer(self, manufacturer: str) -> int:
        pass

    @abstractmethod
    async def list_by_manufacturer(self, manufacturer: str, limit: int = 10) -> List[RecallDTO]:
        pass
