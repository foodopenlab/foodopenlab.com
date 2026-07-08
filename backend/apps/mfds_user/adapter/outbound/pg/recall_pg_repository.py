from datetime import datetime
from typing import Optional, List, Any, cast
from sqlalchemy import desc, func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.dtos.recall_dto import RecallDTO
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.adapter.outbound.orm.recall_orm import RecallModel

_CATEGORY_TYPE_HINTS = {
    "수입식품": ("수입",),
    "식육가공품": ("식육", "육류"),
    "곡류가공품": ("곡",),
    "조미식품": ("조미",),
    "건강간편식": ("건강", "간편"),
    "당류가공품": ("당", "잼", "과자", "빵"),
    "유가공품": ("유가", "유제품", "가공"),
}

def category_filter_clause(category: str):
    cat = category.strip()
    if not cat or cat == "전체":
        return None
    parts = [cast(Any, RecallModel.food_category) == cat]
    for hint in _CATEGORY_TYPE_HINTS.get(cat, ()):
        parts.append(cast(Any, RecallModel.food_type).ilike(f"%{hint}%"))
    return or_(*parts)

def food_type_filter_clause(keyword: str):
    kw = keyword.strip()
    if not kw:
        return None
    if kw in _CATEGORY_TYPE_HINTS or kw == "전체":
        cat_clause = category_filter_clause(kw)
        if cat_clause is not None:
            return cat_clause
    return or_(
        cast(Any, RecallModel.food_type).ilike(f"%{kw}%"),
        cast(Any, RecallModel.food_category).ilike(f"%{kw}%"),
    )

def to_dto(m: RecallModel) -> RecallDTO:
    prdlst_report_no = None
    if m.raw_json and isinstance(m.raw_json, dict):
        prdlst_report_no = (
            m.raw_json.get("PRDLST_REPORT_NO")
            or m.raw_json.get("prdlst_report_no")
            or m.raw_json.get("PRDLST_REPORT_NOT")
        )
    return RecallDTO(
        id=m.id,
        product_name=m.product_name,
        manufacturer=m.manufacturer,
        food_type=m.food_type,
        food_category=m.food_category,
        recall_reason=m.recall_reason,
        recall_grade=m.recall_grade,
        recall_method=m.recall_method,
        registered_at=m.registered_at,
        image_url=m.image_url,
        prdlst_report_no=prdlst_report_no,
    )

class RecallPgRepository(RecallRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, recall_id: str) -> Optional[RecallDTO]:
        row = await self.session.get(RecallModel, recall_id)
        return to_dto(row) if row else None

    async def count_all(self) -> int:
        res = await self.session.execute(select(func.count()).select_from(RecallModel))
        return int(res.scalar_one())

    async def list_distinct_food_types(self) -> List[str]:
        stmt = (
            select(cast(Any, RecallModel.food_type))
            .where(cast(Any, RecallModel.food_type).isnot(None))
            .where(cast(Any, RecallModel.food_type) != "")
            .distinct()
            .order_by(cast(Any, RecallModel.food_type))
        )
        res = await self.session.execute(stmt)
        return [str(row).strip() for row in res.scalars().all() if str(row).strip()]

    def _apply_category_grade(self, stmt, food_category: Optional[str], grade: Optional[int]):
        cat = (food_category or "").strip()
        if cat and cat != "전체":
            clause = category_filter_clause(cat)
            if clause is not None:
                stmt = stmt.where(clause)
        if grade is not None:
            stmt = stmt.where(cast(Any, RecallModel.recall_grade) == grade)
        return stmt

    def _order_latest(self, stmt):
        return stmt.order_by(
            desc(cast(Any, RecallModel.registered_at)).nulls_last(),
            desc(cast(Any, RecallModel.fetched_at)),
            cast(Any, RecallModel.id),
        )

    async def count_list(self, food_category: Optional[str] = None, grade: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(RecallModel)
        stmt = self._apply_category_grade(stmt, food_category, grade)
        res = await self.session.execute(stmt)
        return int(res.scalar_one())

    async def get_list(
        self,
        food_category: Optional[str] = None,
        grade: Optional[int] = None,
        page: int = 1,
        size: int = 20,
        offset: Optional[int] = None,
    ) -> List[RecallDTO]:
        stmt = select(RecallModel)
        stmt = self._apply_category_grade(stmt, food_category, grade)
        skip = offset if offset is not None else (page - 1) * size
        stmt = self._order_latest(stmt).offset(max(0, skip)).limit(size)
        res = await self.session.execute(stmt)
        return [to_dto(m) for m in res.scalars().all()]

    async def get_latest_by_category(
        self,
        food_category: str,
        grade: Optional[int] = None,
        limit: int = 5,
    ) -> List[RecallDTO]:
        stmt = select(RecallModel)
        stmt = self._apply_category_grade(stmt, food_category, grade)
        stmt = self._order_latest(stmt).limit(max(1, limit))
        res = await self.session.execute(stmt)
        return [to_dto(m) for m in res.scalars().all()]

    async def get_latest_by_food_type(
        self,
        keyword: str,
        grade: Optional[int] = None,
        limit: int = 5,
    ) -> List[RecallDTO]:
        stmt = select(RecallModel)
        clause = food_type_filter_clause(keyword)
        if clause is not None:
            stmt = stmt.where(clause)
        if grade is not None:
            stmt = stmt.where(cast(Any, RecallModel.recall_grade) == grade)
        stmt = self._order_latest(stmt).limit(max(1, limit))
        res = await self.session.execute(stmt)
        return [to_dto(m) for m in res.scalars().all()]

    async def count_by_manufacturer(self, manufacturer: str) -> int:
        name = (manufacturer or "").strip()
        if not name:
            return 0
        stmt = select(func.count()).select_from(RecallModel).where(cast(Any, RecallModel.manufacturer).ilike(f"%{name}%"))
        res = await self.session.execute(stmt)
        return int(res.scalar_one())

    async def list_by_manufacturer(self, manufacturer: str, limit: int = 10) -> List[RecallDTO]:
        name = (manufacturer or "").strip()
        if not name:
            return []
        stmt = (
            select(RecallModel)
            .where(cast(Any, RecallModel.manufacturer).ilike(f"%{name}%"))
            .order_by(desc(cast(Any, RecallModel.fetched_at)), cast(Any, RecallModel.id))
            .limit(max(1, min(limit, 50)))
        )
        res = await self.session.execute(stmt)
        return [to_dto(m) for m in res.scalars().all()]
