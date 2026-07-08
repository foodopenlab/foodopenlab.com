from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from mfds_user.app.ports.input.enforcement_use_case import EnforcementUseCase
from mfds_user.app.ports.output.enforcement_repository import EnforcementRepositoryPort
from mfds_user.app.ports.output.enforcement_cache_port import EnforcementCachePort
from mfds_user.app.dtos.enforcement_dto import (
    EnforcementListQuery,
    EnforcementListDTO,
    EnforcementDTO,
    LatestSanctionItemDTO,
    LatestSanctionsDTO,
)

class EnforcementInteractor(EnforcementUseCase):
    def __init__(self, enforcement_repository: EnforcementRepositoryPort, cache_port: EnforcementCachePort) -> None:
        self._repo = enforcement_repository
        self._cache_port = cache_port

    async def list_enforcements(self, query: EnforcementListQuery) -> EnforcementListDTO:
        rows = await self._repo.get_list(
            process_type=query.process_type,
            business_name=query.business_name,
            page=query.page,
            size=query.size
        )
        total = await self._repo.count_list(
            process_type=query.process_type,
            business_name=query.business_name
        )

        empty_label = None
        if total == 0 and query.business_name:
            empty_label = f"'{query.business_name}' 관련 행정처분 사실이 없습니다."

        try:
            sync = self._cache_port.get_public_sync_state()
        except Exception:
            sync = {}

        return EnforcementListDTO(
            total=total,
            page=query.page,
            items=rows,
            empty_label=empty_label,
            last_sync_at=sync.get("last_sync_at"),
            sync_wave=sync.get("sync_wave"),
            sync_slot=sync.get("sync_slot")
        )

    async def get_enforcement_detail(self, enforcement_id: str) -> EnforcementDTO:
        detail = await self._repo.get_by_id(enforcement_id)
        if detail is None:
            raise ValueError("행정처분 정보를 찾을 수 없습니다.")
        return detail

    async def latest_sanctions(self) -> LatestSanctionsDTO:
        try:
            items, fetched_at, is_today, matched_date = self._cache_port.get_latest_sanctions_cache()
        except ValueError as e:
            raise ValueError(f"행정처분 정보 조회 실패: {e}") from e
        except Exception as e:
            raise ValueError(f"행정처분 정보 조회 실패: {e}") from e

        sync = self._cache_port.get_public_sync_state()
        query_date = datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()

        item_dtos = [
            LatestSanctionItemDTO(
                business_name=row.get("business_name", ""),
                industry=row.get("industry", ""),
                disposition_date=row.get("disposition_date", ""),
                disposition_start=row.get("disposition_start", ""),
                disposition_type=row.get("disposition_type", ""),
                violation=row.get("violation", ""),
                address=row.get("address", ""),
                representative=row.get("representative", ""),
                disposition_detail=row.get("disposition_detail", ""),
                agency=row.get("agency", ""),
                serial_no=row.get("serial_no", ""),
                category=row.get("category", ""),
                service_id=row.get("service_id", ""),
            )
            for row in items
        ]

        return LatestSanctionsDTO(
            items=item_dtos,
            fetched_at=fetched_at.isoformat() if fetched_at else None,
            query_date=query_date,
            is_today=is_today,
            matched_date=matched_date,
            last_sync_at=sync.get("last_sync_at"),
            sync_wave=sync.get("sync_wave"),
            sync_slot=sync.get("sync_slot"),
        )
