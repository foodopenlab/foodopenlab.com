from abc import ABC, abstractmethod
from typing import List
from mfds_user.app.dtos.recall_dto import RecallListQuery, RecallListDTO, RecallDTO, LatestRecallsDTO

class RecallUseCase(ABC):
    @abstractmethod
    async def list_recalls(self, query: RecallListQuery) -> RecallListDTO:
        pass

    @abstractmethod
    async def list_food_types(self) -> List[str]:
        pass

    @abstractmethod
    async def get_recall_detail(self, recall_id: str) -> RecallDTO:
        pass

    @abstractmethod
    async def latest_recalls(self) -> LatestRecallsDTO:
        pass

