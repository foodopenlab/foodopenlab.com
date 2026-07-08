from typing import Protocol, List
from uuid import UUID
from mfds_user.domain.entities.expert_user_industry_entity import ExpertUserIndustry
from mfds_user.domain.entities.industry_category_entity import IndustryCategory

class IndustryUseCase(Protocol):
    async def get_my_industry(self, expert_user_id: UUID) -> List[ExpertUserIndustry]:
        """사용자가 선택한 업종 목록을 반환합니다."""
        ...

    async def update_my_industry(
        self,
        expert_user_id: UUID,
        media_codes: List[str],
        foodtype_selections: List[dict]
    ) -> None:
        """사용자의 업종 설정을 업데이트합니다 (뉴스소스 최대 3개, 식품 대분류 최대 3개, 대분류당 중분류 최대 3개)."""
        ...

    async def get_all_categories(self) -> List[IndustryCategory]:
        """모든 업종 카테고리 마스터 데이터를 반환합니다."""
        ...

    async def update_category_keywords(self, code: str, keywords: List[str]) -> None:
        """특정 카테고리의 분석 키워드를 수정합니다."""
        ...
