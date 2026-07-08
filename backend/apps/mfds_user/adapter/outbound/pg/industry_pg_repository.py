from typing import List
from uuid import UUID, uuid4
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.industry_repository import IndustryRepository
from mfds_user.domain.entities.expert_user_industry_entity import ExpertUserIndustry
from mfds_user.domain.entities.industry_category_entity import IndustryCategory
from mfds_user.domain.value_objects.category_type_vo import CategoryType
from mfds_user.adapter.outbound.orm.industry_category_orm import IndustryCategoryORM
from mfds_user.adapter.outbound.orm.category_keyword_orm import CategoryKeywordORM
from mfds_user.adapter.outbound.orm.expert_user_industry_orm import ExpertUserIndustryORM

class IndustryPgRepository(IndustryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_user(self, expert_user_id: UUID) -> List[ExpertUserIndustry]:
        stmt = select(ExpertUserIndustryORM).where(ExpertUserIndustryORM.expert_user_id == expert_user_id)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [
            ExpertUserIndustry(
                id=r.id,
                expert_user_id=r.expert_user_id,
                category_code=r.category_code,
                created_at=r.created_at
            )
            for r in rows
        ]

    async def delete_by_user(self, expert_user_id: UUID) -> None:
        stmt = delete(ExpertUserIndustryORM).where(ExpertUserIndustryORM.expert_user_id == expert_user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def save(self, selection: ExpertUserIndustry) -> None:
        db_item = ExpertUserIndustryORM(
            id=selection.id,
            expert_user_id=selection.expert_user_id,
            category_code=selection.category_code,
            created_at=selection.created_at
        )
        self.session.add(db_item)
        await self.session.commit()

    async def find_all_categories(self) -> List[IndustryCategory]:
        # Fetch categories
        stmt = select(IndustryCategoryORM)
        res = await self.session.execute(stmt)
        categories = res.scalars().all()

        # Fetch all keywords
        kw_stmt = select(CategoryKeywordORM)
        kw_res = await self.session.execute(kw_stmt)
        keywords = kw_res.scalars().all()

        # Group keywords
        kw_map = {}
        for k in keywords:
            kw_map.setdefault(k.category_code, []).append(k.keyword)

        return [
            IndustryCategory(
                code=c.code,
                type=CategoryType(c.type),
                parent_code=c.parent_code,
                depth=c.depth,
                is_flat=c.is_flat,
                name_ko=c.name_ko,
                crawler_param=c.crawler_param,
                keywords=kw_map.get(c.code, [])
            )
            for c in categories
        ]

    async def find_by_codes(self, codes: List[str]) -> List[IndustryCategory]:
        if not codes:
            return []
        # Fetch categories
        stmt = select(IndustryCategoryORM).where(IndustryCategoryORM.code.in_(codes))
        res = await self.session.execute(stmt)
        categories = res.scalars().all()

        # Fetch keywords
        kw_stmt = select(CategoryKeywordORM).where(CategoryKeywordORM.category_code.in_(codes))
        kw_res = await self.session.execute(kw_stmt)
        keywords = kw_res.scalars().all()

        # Group keywords
        kw_map = {}
        for k in keywords:
            kw_map.setdefault(k.category_code, []).append(k.keyword)

        return [
            IndustryCategory(
                code=c.code,
                type=CategoryType(c.type),
                parent_code=c.parent_code,
                depth=c.depth,
                is_flat=c.is_flat,
                name_ko=c.name_ko,
                crawler_param=c.crawler_param,
                keywords=kw_map.get(c.code, [])
            )
            for c in categories
        ]

    async def update_keywords(self, code: str, keywords: List[str]) -> None:
        # Delete existing keywords
        del_stmt = delete(CategoryKeywordORM).where(CategoryKeywordORM.category_code == code)
        await self.session.execute(del_stmt)

        # Insert new keywords
        for kw in keywords:
            db_kw = CategoryKeywordORM(
                id=uuid4(),
                category_code=code,
                keyword=kw
            )
            self.session.add(db_kw)

        await self.session.commit()
