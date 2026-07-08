from abc import ABC, abstractmethod
from typing import Optional

class HaccpPublicApiPort(ABC):
    @abstractmethod
    async def fetch_haccp_product_info(self, business_name: str, product_name: str) -> Optional[dict]:
        """식품안전나라 API로부터 실시간 HACCP 인증원 생산제품 정보를 조회합니다."""
        pass

class HaccpSyncPort(ABC):
    @abstractmethod
    async def sync_haccp_certifications_to_db(self, max_items_per_service: int = 50000) -> int:
        """식품안전나라 API로부터 HACCP 지정 현황 데이터를 DB 캐시에 동기화합니다."""
        pass
