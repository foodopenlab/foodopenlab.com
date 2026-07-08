from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional, List

@dataclass(frozen=True)
class ApiUsageLogDTO:
    id: UUID
    actor_type: str
    actor_id: UUID
    api_name: str
    called_at: datetime
    response_time_ms: int
    status_code: int
    response_ms: int
    is_cache_hit: bool = False
    endpoint: Optional[str] = None

@dataclass(frozen=True)
class SearchLogDTO:
    id: UUID
    actor_type: str
    actor_id: UUID
    keyword: str
    query_pattern: str
    searched_at: datetime
