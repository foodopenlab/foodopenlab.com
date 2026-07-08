from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.external_api.feedback_analysis_llm_adapter import FeedbackAnalysisLLMAdapter
from mfds_user.adapter.outbound.pg.daily_report_pg_repository import DailyReportPgRepository
from mfds_user.adapter.outbound.pg.report_feedback_pg_repository import ReportFeedbackPgRepository
from mfds_user.app.ports.input.report_feedback_use_case import ReportFeedbackUseCase
from mfds_user.app.ports.output.daily_report_repository import DailyReportRepository
from mfds_user.app.ports.output.report_feedback_repository import (
    FeedbackAnalysisLLMPort,
    ReportFeedbackRepository,
)
from mfds_user.app.use_cases.report_feedback_interactor import ReportFeedbackInteractor


def get_report_feedback_repository(
    db: AsyncSession = Depends(get_db),
) -> ReportFeedbackRepository:
    return ReportFeedbackPgRepository(session=db)


def get_daily_report_repository_for_feedback(
    db: AsyncSession = Depends(get_db),
) -> DailyReportRepository:
    return DailyReportPgRepository(session=db)


def get_feedback_analysis_llm_port() -> FeedbackAnalysisLLMPort:
    return FeedbackAnalysisLLMAdapter()


def get_report_feedback_use_case(
    feedback_repo: ReportFeedbackRepository = Depends(get_report_feedback_repository),
    report_repo: DailyReportRepository = Depends(get_daily_report_repository_for_feedback),
    llm_port: FeedbackAnalysisLLMPort = Depends(get_feedback_analysis_llm_port),
) -> ReportFeedbackUseCase:
    return ReportFeedbackInteractor(
        feedback_repo=feedback_repo,
        report_repo=report_repo,
        llm_port=llm_port,
    )
