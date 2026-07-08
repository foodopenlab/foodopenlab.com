from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from mfds_admin.app.dtos.logs_dto import ApiUsageLogDTO, SearchLogDTO

class LogsUseCase(ABC):
    @abstractmethod
    async def list_api_logs(self, page: int, size: int, api_name: Optional[str] = None) -> Tuple[List[ApiUsageLogDTO], int]:
        pass

    @abstractmethod
    async def list_search_logs(self, page: int, size: int, query_pattern: Optional[str] = None) -> Tuple[List[SearchLogDTO], int]:
        pass

    @abstractmethod
    async def get_dashboard_stats(self) -> dict:
        pass

    @abstractmethod
    async def get_api_stats(self, period: str = "today") -> dict:
        pass

