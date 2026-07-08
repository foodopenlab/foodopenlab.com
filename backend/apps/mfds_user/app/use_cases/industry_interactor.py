from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from mfds_user.app.ports.input.industry_use_case import IndustryUseCase
from mfds_user.app.ports.output.industry_repository import IndustryRepository
from mfds_user.domain.entities.expert_user_industry_entity import ExpertUserIndustry
from mfds_user.domain.entities.industry_category_entity import IndustryCategory

class IndustryInteractor(IndustryUseCase):
    MIN_MEDIA = 1
    MAX_MEDIA = 3
    MIN_FT_PARENT = 1
    MAX_FT_PARENT = 3
    MAX_FT_CHILD = 3

    def __init__(self, repo: IndustryRepository) -> None:
        self.repo = repo

    async def get_my_industry(self, expert_user_id: UUID) -> List[ExpertUserIndustry]:
        return await self.repo.find_by_user(expert_user_id)

    async def update_my_industry(
        self,
        expert_user_id: UUID,
        media_codes: List[str],
        foodtype_selections: List[dict]
    ) -> None:
        # 1. 미디어 1~3개 검증
        if len(media_codes) < self.MIN_MEDIA:
            raise ValueError("뉴스 소스는 최소 1개 이상 선택해야 합니다.")
        if len(media_codes) > self.MAX_MEDIA:
            raise ValueError("뉴스 소스는 최대 3개까지 선택 가능합니다.")

        # 2. 식품유형 대분류 1~3개 검증
        parent_codes = {
            s["parent_code"] if s["parent_code"] else s["code"]
            for s in foodtype_selections
        }
        if len(parent_codes) < self.MIN_FT_PARENT:
            raise ValueError("식품 유형은 최소 1개 이상 선택해야 합니다.")
        if len(parent_codes) > self.MAX_FT_PARENT:
            raise ValueError("식품 유형은 최대 3개까지 선택 가능합니다.")

        # 3. 대분류별 중분류 최대 3개 검증
        for parent in parent_codes:
            children = [
                s for s in foodtype_selections
                if s["parent_code"] == parent
            ]
            if len(children) > self.MAX_FT_CHILD:
                raise ValueError("대분류당 중분류는 최대 3개까지 선택 가능합니다.")

        # 4. 기존 업종 선택 내역 전체 삭제 (PUT 시맨틱)
        await self.repo.delete_by_user(expert_user_id)

        # 5. 미디어 소스 저장
        for code in media_codes:
            await self.repo.save(ExpertUserIndustry(
                id=uuid4(),
                expert_user_id=expert_user_id,
                category_code=code,
                created_at=datetime.utcnow()
            ))

        # 6. 식품유형 저장
        for sel in foodtype_selections:
            await self.repo.save(ExpertUserIndustry(
                id=uuid4(),
                expert_user_id=expert_user_id,
                category_code=sel["code"],
                created_at=datetime.utcnow()
            ))

    async def get_all_categories(self) -> List[IndustryCategory]:
        return await self.repo.find_all_categories()

    async def update_category_keywords(self, code: str, keywords: List[str]) -> None:
        await self.repo.update_keywords(code, keywords)
