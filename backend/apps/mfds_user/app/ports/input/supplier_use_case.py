from abc import ABC, abstractmethod
from mfds_user.app.dtos.supplier_dto import SupplierRiskCardDTO

class SupplierUseCase(ABC):
    @abstractmethod
    async def get_supplier_risk_card(self, business_name: str, limit: int = 10) -> SupplierRiskCardDTO:
        pass
