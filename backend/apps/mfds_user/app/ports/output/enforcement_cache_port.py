from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Tuple, Optional

class EnforcementCachePort(ABC):
    @abstractmethod
    def get_latest_sanctions_cache(self) -> Tuple[List[dict], Optional[datetime], bool, Optional[str]]:
        """최신 행정처분 디스크 캐시 및 관련 메타데이터를 반환합니다.
        
        Returns:
            Tuple[items, fetched_at, is_today, matched_date]
        """
        pass

    @abstractmethod
    def get_public_sync_state(self) -> dict:
        """공공데이터 동기화 상태 메타데이터를 반환합니다."""
        pass
