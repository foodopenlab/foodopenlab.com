import logging
from mfds_user.app.ports.output.supplier_ports import SupplierPublicApiPort
from mfds_user.app.dtos.supplier_dto import SupplierLicenseBriefDTO

logger = logging.getLogger(__name__)

class SupplierPublicApiAdapter(SupplierPublicApiPort):
    async def fetch_license_search(self, business_name: str) -> SupplierLicenseBriefDTO:
        name = (business_name or "").strip()
        if not name:
            return SupplierLicenseBriefDTO(found=False)

        # 데모용 임시 코드 (레거시 동작 복제)
        if "한빛" in name:
            return SupplierLicenseBriefDTO(
                found=True,
                status="영업중",
                business_type="식품제조가공업",
                license_number="123-45-67890",
                demo=True,
            )

        return SupplierLicenseBriefDTO(found=False)
