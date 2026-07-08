from typing import Protocol, List
from uuid import UUID
from mfds_user.domain.entities.expert_user_industry_entity import ExpertUserIndustry
from mfds_user.domain.entities.industry_category_entity import IndustryCategory

class IndustryRepository(Protocol):
    async def find_by_user(self, expert_user_id: UUID) -> List[ExpertUserIndustry]:
        ...

    async def delete_by_user(self, expert_user_id: UUID) -> None:
        ...

    async def save(self, selection: ExpertUserIndustry) -> None:
        ...

    async def find_all_categories(self) -> List[IndustryCategory]:
        ...

    async def find_by_codes(self, codes: List[str]) -> List[IndustryCategory]:
        ...

    async def update_keywords(self, code: str, keywords: List[str]) -> None:
        ...
