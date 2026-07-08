from typing import Optional
from mfds_user.app.ports.input.haccp_use_case import HaccpUseCase
from mfds_user.app.ports.output.haccp_repository import HaccpRepositoryPort
from mfds_user.app.dtos.haccp_dto import HaccpProductInfoDTO

class HaccpInteractor(HaccpUseCase):
    def __init__(self, haccp_repository: HaccpRepositoryPort) -> None:
        self._repo = haccp_repository

    async def get_product_info(self, prdlst_report_no: Optional[str], product_name: Optional[str]) -> HaccpProductInfoDTO:
        pr = (prdlst_report_no or "").strip()
        pn = (product_name or "").strip()

        if pr == "20180501001234":
            return HaccpProductInfoDTO(
                found=True,
                prdlst_report_no=pr,
                product_name=pn or "프리미엄 그릭요거트 플레인",
                manufacturer="한빛유가공 (데모)",
                raw_materials=["원유", "유산균", "설탕", "팩틴", "천연향료", "비타민D"],
                allergens=["우유", "대두"],
                nutrient_info="나트륨 45mg, 탄수화물 12g, 당류 8g, 단백질 9g, 지방 3.2g (100g당, 데모)",
                image_urls=["https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&q=80"],
                barcode="8801234567890",
            )

        res = await self._repo.fetch_product_info_from_external_api(pr, pn)
        if not res.found and pr == "20180501001234":
            return HaccpProductInfoDTO(
                found=True,
                prdlst_report_no=pr,
                product_name=pn or "프리미엄 그릭요거트 플레인",
                manufacturer="한빛유가공 (데모)",
                raw_materials=["원유", "유산균", "설탕", "팩틴", "천연향료", "비타민D"],
                allergens=["우유", "대두"],
                nutrient_info="나트륨 45mg, 탄수화물 12g, 당류 8g, 단백질 9g, 지방 3.2g (100g당, 데모)",
                image_urls=["https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&q=80"],
                barcode="8801234567890",
            )
        return res
