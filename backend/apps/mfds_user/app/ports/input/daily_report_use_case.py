from typing import Protocol, List
from uuid import UUID
from datetime import date
from mfds_user.domain.entities.daily_report_entity import DailyReport

class DailyReportUseCase(Protocol):
    async def get_my_reports(self, expert_user_id: UUID) -> List[DailyReport]:
        ...

    async def get_report_detail(self, expert_user_id: UUID, report_id: UUID) -> DailyReport:
        ...

    async def generate(self, expert_user_id: UUID) -> DailyReport:
        ...

    async def generate_for_date(self, expert_user_id: UUID, report_date: date, force_refresh: bool = False) -> DailyReport:
        ...

    async def save_report(self, expert_user_id: UUID, report_id: UUID) -> DailyReport:
        ...
