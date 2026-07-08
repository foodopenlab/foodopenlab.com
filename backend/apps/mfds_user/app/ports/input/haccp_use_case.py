from abc import ABC, abstractmethod
from typing import Optional
from mfds_user.app.dtos.haccp_dto import HaccpProductInfoDTO

class HaccpUseCase(ABC):
    @abstractmethod
    async def get_product_info(self, prdlst_report_no: Optional[str], product_name: Optional[str]) -> HaccpProductInfoDTO:
        pass
