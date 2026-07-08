from abc import ABC, abstractmethod
from typing import Optional

class SearchLoggerPort(ABC):
    @abstractmethod
    async def log_search(
        self,
        user_id: Optional[str],
        session_key: Optional[str],
        search_type: str,
        query_keyword: str,
    ) -> None:
        pass
