from datetime import datetime
from typing import Optional, List, Any, cast
from sqlalchemy import desc, func, select, or_, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.dtos.enforcement_dto import EnforcementDTO
from mfds_user.app.ports.output.enforcement_repository import EnforcementRepositoryPort
from mfds_user.adapter.outbound.orm.enforcement_orm import EnforcementModel

PROCESS_TYPE_LABELS = ("영업정지", "영업취소", "과징금", "시정명령")

def process_type_filter_clause(process_type: str):
    pt = (process_type or "").strip()
    if not pt or pt == "전체":
        return None
    if pt == "기타":
        main_match = or_(
            *[cast(Any, EnforcementModel.process_type).ilike(f"%{label}%") for label in PROCESS_TYPE_LABELS]
        )
        return or_(
            cast(Any, EnforcementModel.process_type) == "기타",
            cast(Any, EnforcementModel.process_type).is_(None),
            cast(Any, EnforcementModel.process_type) == "",
            and_(cast(Any, EnforcementModel.process_type).isnot(None), not_(main_match)),
        )
    parts = [
        cast(Any, EnforcementModel.process_type) == pt,
        cast(Any, EnforcementModel.process_type).ilike(f"%{pt}%"),
    ]
    for label in PROCESS_TYPE_LABELS:
        if label in pt:
            parts.append(cast(Any, EnforcementModel.process_type).ilike(f"%{label}%"))
    return or_(*parts)

def to_dto(m: EnforcementModel) -> EnforcementDTO:
    return EnforcementDTO(
        id=m.id,
        business_name=m.business_name,
        business_type=m.business_type,
        address=m.address,
        process_type=m.process_type,
        violation_content=m.violation_content,
        violation_date=m.violation_date,
        process_date=m.process_date,
        district=m.district,
    )

class EnforcementPgRepository(EnforcementRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, enforcement_id: str) -> Optional[EnforcementDTO]:
        row = await self.session.get(EnforcementModel, enforcement_id)
        return to_dto(row) if row else None

    async def count_all(self) -> int:
        res = await self.session.execute(select(func.count()).select_from(EnforcementModel))
        return int(res.scalar_one())

    def _list_filters(self, process_type: Optional[str], business_name: Optional[str]):
        stmt = select(EnforcementModel)
        pt = (process_type or "").strip()
        if pt and pt != "전체":
            clause = process_type_filter_clause(pt)
            if clause is not None:
                stmt = stmt.where(clause)
        name = (business_name or "").strip()
        if name:
            stmt = stmt.where(cast(Any, EnforcementModel.business_name).ilike(f"%{name}%"))
        return stmt

    def _order_latest(self, stmt):
        return stmt.order_by(
            desc(cast(Any, EnforcementModel.process_date)).nulls_last(),
            desc(cast(Any, EnforcementModel.fetched_at)),
            cast(Any, EnforcementModel.id),
        )

    async def count_list(self, process_type: Optional[str] = None, business_name: Optional[str] = None) -> int:
        subq = self._list_filters(process_type, business_name).subquery()
        stmt = select(func.count()).select_from(subq)
        res = await self.session.execute(stmt)
        return int(res.scalar_one())

    async def get_list(
        self,
        process_type: Optional[str] = None,
        business_name: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> List[EnforcementDTO]:
        stmt = self._list_filters(process_type, business_name)
        skip = (page - 1) * size
        stmt = self._order_latest(stmt).offset(max(0, skip)).limit(max(1, size))
        res = await self.session.execute(stmt)
        return [to_dto(m) for m in res.scalars().all()]
