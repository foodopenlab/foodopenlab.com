from abc import ABC, abstractmethod
from typing import Optional, List, Any
from mfds_user.app.dtos.haccp_dto import HaccpProductInfoDTO

class HaccpRepositoryPort(ABC):
    @abstractmethod
    async def fetch_product_info_from_external_api(
        self,
        prdlst_report_no: Optional[str],
        product_name: Optional[str]
    ) -> HaccpProductInfoDTO:
        pass

    @abstractmethod
    async def find_for_supplier(
        self,
        business_name: str,
        license_number: Optional[str],
        limit: int = 50
    ) -> List[Any]:
        pass

