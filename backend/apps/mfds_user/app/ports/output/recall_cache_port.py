from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Optional, Any

class RecallCachePort(ABC):
    @abstractmethod
    def get_latest_recalls_cache(self) -> Tuple[List[dict], Optional[datetime], bool, Optional[str]]:
        """최신 위해식품 회수 목록 디스크 캐시 및 관련 메타데이터를 반환합니다.
        
        Returns:
            Tuple[items, fetched_at, is_today, matched_date]
        """
        pass

    @abstractmethod
    def get_public_sync_state(self) -> dict:
        """공공데이터 동기화 상태 메타데이터를 반환합니다."""
        pass

    @abstractmethod
    def list_distinct_food_types_from_disk(self) -> List[str]:
        """디스크 캐시로부터 고유한 식품 유형 목록을 반환합니다."""
        pass
