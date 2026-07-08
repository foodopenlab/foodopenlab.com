from fastapi import APIRouter, Depends, HTTPException, status
from mfds_user.app.ports.input.supplier_use_case import SupplierUseCase
from mfds_user.dependencies.supplier import get_supplier_use_case
from mfds_user.adapter.inbound.api.schemas.supplier_schema import (
    SupplierRiskCardResponse,
    SupplierRiskRecallBrief,
    SupplierRiskEnforcementBrief,
    SupplierLicenseBrief,
    SupplierHaccpCertificationBrief
)

router = APIRouter(prefix="/supplier", tags=["supplier"])

@router.get("/risk-card", response_model=SupplierRiskCardResponse)
async def supplier_risk_card(
    business_name: str,
    limit: int = 10,
    use_case: SupplierUseCase = Depends(get_supplier_use_case)
) -> SupplierRiskCardResponse:
    res = await use_case.get_supplier_risk_card(business_name=business_name, limit=limit)

    recalls = [
        SupplierRiskRecallBrief(
            id=r.id,
            product_name=r.product_name,
            manufacturer=r.manufacturer,
            recall_grade=r.recall_grade,
            registered_at=r.registered_at,
            recall_reason=r.recall_reason
        )
        for r in res.recalls
    ]
    enforcements = [
        SupplierRiskEnforcementBrief(
            id=e.id,
            business_name=e.business_name,
            process_type=e.process_type,
            process_date=e.process_date,
            violation_content=e.violation_content
        )
        for e in res.enforcements
    ]

    license_brief = None
    if res.license:
        license_brief = SupplierLicenseBrief(
            found=res.license.found,
            status=res.license.status,
            business_type=res.license.business_type,
            license_number=res.license.license_number,
            demo=res.license.demo
        )

    haccp_brief = None
    if res.haccp_certification:
        haccp_brief = SupplierHaccpCertificationBrief(
            found=res.haccp_certification.found,
            certified=res.haccp_certification.certified,
            certificate_number=res.haccp_certification.certificate_number,
            expiry_date=res.haccp_certification.expiry_date,
            designated_date=res.haccp_certification.designated_date,
            certified_products=res.haccp_certification.certified_products,
            demo=res.haccp_certification.demo
        )

    return SupplierRiskCardResponse(
        business_name=res.business_name,
        overall_risk=res.overall_risk,
        summary=res.summary,
        recall_count=res.recall_count,
        enforcement_count=res.enforcement_count,
        recalls=recalls,
        enforcements=enforcements,
        license=license_brief,
        haccp_certification=haccp_brief
    )
