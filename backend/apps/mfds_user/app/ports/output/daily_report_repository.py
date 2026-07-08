from typing import Protocol, List, Optional
from uuid import UUID
from datetime import date
from mfds_user.domain.entities.daily_report_entity import DailyReport

class DailyReportRepository(Protocol):
    async def find_by_user(self, expert_user_id: UUID) -> List[DailyReport]:
        ...

    async def find_by_user_and_date(self, expert_user_id: UUID, report_date: date) -> Optional[DailyReport]:
        ...

    async def find(self, report_id: UUID) -> Optional[DailyReport]:
        ...

    async def save(self, report: DailyReport) -> DailyReport:
        ...

    async def update(self, report: DailyReport) -> DailyReport:
        ...

    async def delete_expired_unsaved(self, expert_user_id: UUID) -> None:
        ...

    async def delete_by_user_and_date(self, expert_user_id: UUID, report_date: date) -> bool:
        """당일 리포트 삭제(수동 재생성용). 삭제 시 True."""
        ...
