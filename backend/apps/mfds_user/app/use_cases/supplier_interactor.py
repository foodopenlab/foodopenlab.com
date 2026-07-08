import logging
from typing import List, Optional
import asyncio
from mfds_user.app.ports.input.supplier_use_case import SupplierUseCase
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.app.ports.output.enforcement_repository import EnforcementRepositoryPort
from mfds_user.app.ports.output.haccp_repository import HaccpRepositoryPort
from mfds_user.app.ports.output.supplier_ports import SupplierPublicApiPort
from mfds_user.app.dtos.supplier_dto import (
    SupplierRiskCardDTO,
    SupplierRiskRecallBriefDTO,
    SupplierRiskEnforcementBriefDTO,
    SupplierLicenseBriefDTO,
    SupplierHaccpCertificationBriefDTO,
    RiskLevel
)

logger = logging.getLogger(__name__)

_HIGH_PROCESS = frozenset({"영업정지", "영업취소"})
_MEDIUM_PROCESS = frozenset({"과징금", "시정명령"})

def _compute_risk(
    *,
    recall_count: int,
    max_grade: Optional[int],
    enforcement_count: int,
    has_high_process: bool,
    has_medium_process: bool,
    license_status: Optional[str],
) -> tuple[RiskLevel, str]:
    if license_status == "폐업":
        return "HIGH", "인허가 상태가 폐업으로 확인되었습니다."

    if has_high_process or (max_grade is not None and max_grade <= 1):
        return "HIGH", "1등급 회수 또는 영업정지·영업취소 등 중대 처분이 있습니다."

    if has_medium_process or (max_grade == 2) or recall_count >= 2 or enforcement_count >= 2:
        return "MEDIUM", "2등급 회수·과징금·시정명령 또는 복수 이력이 있습니다."

    if recall_count > 0 or enforcement_count > 0:
        return "LOW", "경미한 회수·처분 이력이 있습니다."

    return "NONE", "캐시 DB 기준 관련 회수·행정처분 이력이 없습니다."

def _current_haccp_rows(rows: list, *, license_number: str | None) -> list:
    active_rows = [row for row in rows if row.is_active]
    if license_number or not active_rows:
        return active_rows or rows

    latest_designated_date = max((row.designated_date or "") for row in active_rows)
    if not latest_designated_date:
        return active_rows
    return [row for row in active_rows if (row.designated_date or "") == latest_designated_date]

class SupplierInteractor(SupplierUseCase):
    def __init__(
        self,
        recall_repository: RecallRepositoryPort,
        enforcement_repository: EnforcementRepositoryPort,
        haccp_repository: HaccpRepositoryPort,
        supplier_public_api: SupplierPublicApiPort,
    ) -> None:
        self._recall_repo = recall_repository
        self._enforcement_repo = enforcement_repository
        self._haccp_repo = haccp_repository
        self._supplier_public_api = supplier_public_api

    async def _haccp_certification_for_supplier(
        self,
        *,
        business_name: str,
        license_number: Optional[str],
    ) -> SupplierHaccpCertificationBriefDTO:
        rows = await self._haccp_repo.find_for_supplier(
            business_name=business_name,
            license_number=license_number,
            limit=100
        )
        if not rows:
            return SupplierHaccpCertificationBriefDTO(found=False, certified=False, demo=False)

        current_rows = _current_haccp_rows(rows, license_number=license_number)
        products = sorted(
            {
                (row.product_name or row.industry_name or "").strip()
                for row in current_rows
                if (row.product_name or row.industry_name or "").strip()
            }
        )
        first = current_rows[0]
        return SupplierHaccpCertificationBriefDTO(
            found=True,
            certified=any(row.is_active for row in current_rows),
            certificate_number=first.haccp_appn_no,
            expiry_date=first.expiry_date,
            designated_date=first.designated_date,
            certified_products=products[:10],
            demo=False,
        )

    async def get_supplier_risk_card(self, business_name: str, limit: int = 10) -> SupplierRiskCardDTO:
        name = (business_name or "").strip()
        if not name:
            return SupplierRiskCardDTO(
                business_name="",
                overall_risk="NONE",
                summary="업체명을 입력해 주세요.",
            )

        recall_rows = await self._recall_repo.list_by_manufacturer(name, limit=limit)
        recall_count = await self._recall_repo.count_by_manufacturer(name)
        enf_rows = await self._enforcement_repo.get_list(business_name=name, page=1, size=limit)
        enf_count = await self._enforcement_repo.count_list(business_name=name)

        recalls = [
            SupplierRiskRecallBriefDTO(
                id=r.id,
                product_name=r.product_name,
                manufacturer=r.manufacturer,
                recall_grade=r.recall_grade,
                registered_at=r.registered_at,
                recall_reason=r.recall_reason,
            )
            for r in recall_rows
        ]
        enforcements = [
            SupplierRiskEnforcementBriefDTO(
                id=e.id,
                business_name=e.business_name,
                process_type=e.process_type,
                process_date=e.process_date,
                violation_content=e.violation_content,
            )
            for e in enf_rows
        ]

        grades = [r.recall_grade for r in recall_rows if r.recall_grade is not None]
        max_grade = min(grades) if grades else None
        has_high = any((e.process_type or "") in _HIGH_PROCESS for e in enf_rows)
        has_medium = any((e.process_type or "") in _MEDIUM_PROCESS for e in enf_rows)

        license_brief = None
        license_status = None
        license_number = None
        try:
            lic = await self._supplier_public_api.fetch_license_search(name)
            if lic.found:
                license_status = lic.status
                license_number = lic.license_number
                license_brief = lic
            else:
                license_brief = SupplierLicenseBriefDTO(found=False)
        except Exception as e:
            logger.warning("license search for risk card failed: %s", e)
            license_brief = SupplierLicenseBriefDTO(found=False)

        haccp_brief = await self._haccp_certification_for_supplier(
            business_name=name,
            license_number=license_number
        )

        overall, summary = _compute_risk(
            recall_count=recall_count,
            max_grade=max_grade,
            enforcement_count=enf_count,
            has_high_process=has_high,
            has_medium_process=has_medium,
            license_status=license_status,
        )

        return SupplierRiskCardDTO(
            business_name=name,
            overall_risk=overall,
            summary=summary,
            recall_count=recall_count,
            enforcement_count=enf_count,
            recalls=recalls,
            enforcements=enforcements,
            license=license_brief,
            haccp_certification=haccp_brief,
        )
