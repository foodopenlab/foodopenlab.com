from fastapi import APIRouter, Depends, HTTPException, status
from mfds_user.app.ports.input.haccp_use_case import HaccpUseCase
from mfds_user.dependencies.haccp import get_haccp_use_case
from mfds_user.adapter.inbound.api.schemas.haccp_schema import HaccpProductInfoResponse

router = APIRouter(prefix="/haccp-cert", tags=["haccp"])

@router.get("/product-info", response_model=HaccpProductInfoResponse)
async def get_product_info(
    prdlst_report_no: str | None = None,
    product_name: str | None = None,
    use_case: HaccpUseCase = Depends(get_haccp_use_case)
) -> HaccpProductInfoResponse:
    res = await use_case.get_product_info(prdlst_report_no, product_name)
    return HaccpProductInfoResponse(
        found=res.found,
        prdlst_report_no=res.prdlst_report_no,
        product_name=res.product_name,
        manufacturer=res.manufacturer,
        raw_materials=res.raw_materials,
        allergens=res.allergens,
        nutrient_info=res.nutrient_info,
        image_urls=res.image_urls,
        barcode=res.barcode
    )
