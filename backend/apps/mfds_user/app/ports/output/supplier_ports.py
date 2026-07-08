from abc import ABC, abstractmethod
from mfds_user.app.dtos.supplier_dto import SupplierLicenseBriefDTO

class SupplierPublicApiPort(ABC):
    @abstractmethod
    async def fetch_license_search(self, business_name: str) -> SupplierLicenseBriefDTO:
        """업체 인허가 상태 정보를 실시간으로 조회합니다."""
        pass
