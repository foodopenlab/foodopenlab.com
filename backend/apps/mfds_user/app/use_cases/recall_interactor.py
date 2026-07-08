from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from mfds_user.app.ports.input.recall_use_case import RecallUseCase
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.app.ports.output.recall_cache_port import RecallCachePort
from mfds_user.app.dtos.recall_dto import RecallListQuery, RecallListDTO, RecallDTO, LatestRecallsDTO, LatestRecallItemDTO

DISPLAY_FALLBACK_NOTE = "일치하는 카테고리/검색어의 최근 회수 정보가 없어, 전체 최신 위해식품 회수 정보로 대체 표시합니다."

class RecallInteractor(RecallUseCase):
    def __init__(self, recall_repository: RecallRepositoryPort, cache_port: RecallCachePort) -> None:
        self._repo = recall_repository
        self._cache_port = cache_port

    async def list_food_types(self) -> List[str]:
        types = await self._repo.list_distinct_food_types()
        if types:
            return types
        try:
            return self._cache_port.list_distinct_food_types_from_disk()
        except Exception:
            return []

    async def get_recall_detail(self, recall_id: str) -> RecallDTO:
        detail = await self._repo.get_by_id(recall_id)
        if detail is None:
            raise ValueError("회수 정보를 찾을 수 없습니다.")
        return detail

    async def list_recalls(self, query: RecallListQuery) -> RecallListDTO:
        limit = 5
        kw = (query.food_type or "").strip()
        cat = (query.food_category or "").strip()
        grade = query.grade

        if kw:
            rows = await self._repo.get_latest_by_food_type(kw, grade, limit=limit)
            note = None
            if not rows:
                rows = await self._repo.get_list(None, grade, page=1, size=limit)
                note = DISPLAY_FALLBACK_NOTE
            return RecallListDTO(total=len(rows), page=query.page, items=rows, display_note=note)

        if cat and cat != "전체":
            rows = await self._repo.get_latest_by_category(cat, grade, limit=limit)
            note = None
            if not rows:
                rows = await self._repo.get_list(None, grade, page=1, size=limit)
                note = DISPLAY_FALLBACK_NOTE
            return RecallListDTO(total=len(rows), page=query.page, items=rows, display_note=note)

        if query.page <= 1:
            rows = await self._repo.get_list(None, grade, page=1, size=limit)
            total = await self._repo.count_list(None, grade)
            return RecallListDTO(total=total, page=query.page, items=rows, display_note=None)

        total = await self._repo.count_list(None, grade)
        skip = limit + (query.page - 2) * query.size
        items = await self._repo.get_list(None, grade, page=query.page, size=query.size, offset=skip)
        return RecallListDTO(total=total, page=query.page, items=items, display_note=None)

    async def latest_recalls(self) -> LatestRecallsDTO:
        try:
            items, fetched_at, is_today, matched_date = self._cache_port.get_latest_recalls_cache()
        except ValueError as e:
            raise ValueError(f"회수 정보 조회 실패: {e}")
        except Exception as e:
            raise ValueError(f"회수 정보 조회 실패: {e}")

        sync = self._cache_port.get_public_sync_state()
        query_date = datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()

        item_dtos = [
            LatestRecallItemDTO(
                product_name=row.get("product_name", ""),
                reason=row.get("reason", ""),
                business_name=row.get("business_name", ""),
                registered_at=row.get("registered_at", ""),
                recall_grade=row.get("recall_grade", ""),
                food_type=row.get("food_type", ""),
                serial_no=row.get("serial_no", ""),
            )
            for row in items
        ]

        return LatestRecallsDTO(
            items=item_dtos,
            fetched_at=fetched_at.isoformat() if fetched_at else None,
            query_date=query_date,
            is_today=is_today,
            matched_date=matched_date,
            last_sync_at=sync.get("last_sync_at"),
            sync_wave=sync.get("sync_wave"),
            sync_slot=sync.get("sync_slot"),
        )
