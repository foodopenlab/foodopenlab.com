from datetime import date
import logging
from mfds_user.app.ports.input.report_scheduler_use_case import ReportSchedulerUseCase
from mfds_user.app.ports.input.daily_report_use_case import DailyReportUseCase
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.app.ports.output.industry_repository import IndustryRepository

logger = logging.getLogger(__name__)

class ReportSchedulerInteractor(ReportSchedulerUseCase):
    def __init__(
        self,
        auth_repo: AuthRepository,
        industry_repo: IndustryRepository,
        daily_report_use_case: DailyReportUseCase
    ) -> None:
        self.auth_repo = auth_repo
        self.industry_repo = industry_repo
        self.daily_report_use_case = daily_report_use_case

    async def generate_all(self) -> dict:
        users = await self.auth_repo.find_all_active()
        today = date.today()
        success, fail, skipped = 0, 0, 0

        for user in users:
            # 1. Skip if registered today (신규 가입자 당일 발송 제외)
            if user.created_at.date() == today:
                skipped += 1
                continue

            # 2. Skip if no industry selected
            industries = await self.industry_repo.find_by_user(user.id)
            if not industries:
                skipped += 1
                continue

            try:
                await self.daily_report_use_case.generate(user.id)
                success += 1
            except Exception as e:
                fail += 1
                logger.error(f"Report generation failed for user {user.id}: {e}")

        return {
            "success": success,
            "fail":    fail,
            "skipped": skipped,
            "total":   len(users),
        }
