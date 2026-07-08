import asyncio
import re
from typing import Optional, List, Any, cast
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.haccp_repository import HaccpRepositoryPort
from mfds_user.app.dtos.haccp_dto import HaccpProductInfoDTO
from mfds_user.adapter.outbound.haccp.haccp_public_api import fetch_haccp_product_info
from mfds_user.adapter.outbound.orm.haccp_certification_orm import HaccpCertificationModel

def _normalize_business_name(value: str | None) -> str:
    text = (value or "").lower()
    for token in ("주식회사", "(주)", "㈜"):
        text = text.replace(token, "")
    return re.sub(r"[\s().\-_/]+", "", text)

def _digits_only(value: str | None) -> str:
    return re.sub(r"\D+", "", value or "")

class HaccpPgRepository(HaccpRepositoryPort):
    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session

    async def fetch_product_info_from_external_api(
        self,
        prdlst_report_no: Optional[str],
        product_name: Optional[str]
    ) -> HaccpProductInfoDTO:
        def _run():
            return fetch_haccp_product_info(prdlst_report_no, product_name)

        res = await asyncio.to_thread(_run)
        return HaccpProductInfoDTO(
            found=res.get("found", False),
            prdlst_report_no=res.get("prdlst_report_no") or prdlst_report_no or "",
            product_name=res.get("product_name"),
            manufacturer=res.get("manufacturer"),
            raw_materials=res.get("raw_materials", []),
            allergens=res.get("allergens", []),
            nutrient_info=res.get("nutrient_info"),
            image_urls=res.get("image_urls", []),
            barcode=res.get("barcode"),
        )

    async def find_for_supplier(
        self,
        business_name: str,
        license_number: Optional[str],
        limit: int = 50
    ) -> List[Any]:
        if not self.session:
            return []
        
        lic = _digits_only(license_number)
        name = _normalize_business_name(business_name)
        if not lic and not name:
            return []

        if lic:
            stmt = self._ordered_supplier_match_query(
                cast(Any, HaccpCertificationModel.license_number) == lic,
                limit=limit,
            )
            res = await self.session.execute(stmt)
            return list(res.scalars().all())

        stmt = self._ordered_supplier_match_query(
            cast(Any, HaccpCertificationModel.normalized_business_name).ilike(f"%{name}%"),
            limit=limit,
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    def _ordered_supplier_match_query(self, clause, *, limit: int):
        stmt = (
            select(HaccpCertificationModel)
            .where(clause)
            .order_by(
                desc(cast(Any, HaccpCertificationModel.is_active)),
                desc(cast(Any, HaccpCertificationModel.designated_date)).nulls_last(),
                desc(cast(Any, HaccpCertificationModel.expiry_date)).nulls_last(),
                cast(Any, HaccpCertificationModel.id),
            )
            .limit(max(1, min(limit, 100)))
        )
        return stmt
