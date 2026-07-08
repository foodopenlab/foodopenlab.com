from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from datetime import datetime
from mfds_admin.app.dtos.logs_dto import ApiUsageLogDTO, SearchLogDTO

class LogsRepositoryPort(ABC):
    @abstractmethod
    async def get_api_logs(self, page: int, size: int, api_name: Optional[str] = None) -> Tuple[List[ApiUsageLogDTO], int]:
        pass

    @abstractmethod
    async def get_search_logs(self, page: int, size: int, query_pattern: Optional[str] = None) -> Tuple[List[SearchLogDTO], int]:
        pass

    @abstractmethod
    async def get_api_stats_summary(self, start_date: datetime, end_date: datetime) -> dict:
        pass

    @abstractmethod
    async def count_chats_today(self) -> dict:
        pass

    @abstractmethod
    async def count_users_summary(self) -> dict:
        pass

    @abstractmethod
    async def get_api_dashboard_stats(self, start_date: datetime, end_date: datetime) -> dict:
        pass

