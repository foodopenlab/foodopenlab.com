from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.external_api.gov_and_stats_adapters import (
    FisNewsletterCrawlerAdapter,
    MfdsPressAdapter,
    RecallReportAdapter,
)
from mfds_user.adapter.outbound.external_api.news_adapters import (
    CompositeNewsAdapter,
    FoodIconCrawlerAdapter,
    FoodJournalCrawlerAdapter,
    ThinkfoodCrawlerAdapter,
)
from mfds_user.adapter.outbound.external_api.regulation_api_adapter import RegulationApiAdapter
from mfds_user.adapter.outbound.external_api.research_adapters import (
    CompositeResearchAdapter,
    PubMedAdapter,
    ScienceOnAdapter,
)
from mfds_user.adapter.outbound.external_api.risk_and_llm_adapters import FoodRiskAdapter, ReportLLMAdapter
from mfds_user.adapter.outbound.pg.auth_pg_repository import AuthPgRepository
from mfds_user.adapter.outbound.pg.daily_report_pg_repository import DailyReportPgRepository
from mfds_user.adapter.outbound.pg.industry_pg_repository import IndustryPgRepository
from mfds_user.adapter.outbound.pg.recall_pg_repository import RecallPgRepository
from mfds_user.app.ports.input.daily_report_use_case import DailyReportUseCase
from mfds_user.app.ports.input.report_scheduler_use_case import ReportSchedulerUseCase
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.app.ports.output.daily_report_repository import DailyReportRepository
from mfds_user.app.ports.output.industry_repository import IndustryRepository
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.app.use_cases.daily_report_interactor import DailyReportInteractor
from mfds_user.app.use_cases.report_scheduler_interactor import ReportSchedulerInteractor
from mfds_user.dependencies.auth import get_auth_repository
from mfds_user.dependencies.industry import get_industry_repository
from mfds_user.dependencies.recall import get_recall_repository


def _compose_daily_report_interactor(
    report_repo: DailyReportRepository,
    industry_repo: IndustryRepository,
    recall_repo: RecallRepositoryPort,
) -> DailyReportUseCase:
    news_port = CompositeNewsAdapter(
        thinkfood=ThinkfoodCrawlerAdapter(),
        foodjournal=FoodJournalCrawlerAdapter(),
        foodicon=FoodIconCrawlerAdapter(),
    )
    research_port = CompositeResearchAdapter(
        pubmed=PubMedAdapter(),
        scienceon=ScienceOnAdapter(),
    )
    return DailyReportInteractor(
        report_repo=report_repo,
        industry_repo=industry_repo,
        thinkfood_port=news_port,
        mfds_port=MfdsPressAdapter(),
        recall_port=RecallReportAdapter(recall_repo=recall_repo),
        regulation_port=RegulationApiAdapter(),
        risk_port=FoodRiskAdapter(),
        research_port=research_port,
        stats_port=FisNewsletterCrawlerAdapter(),
        llm_port=ReportLLMAdapter(),
    )


def get_daily_report_repository(
    db: AsyncSession = Depends(get_db),
) -> DailyReportRepository:
    return DailyReportPgRepository(session=db)


def get_daily_report_use_case(
    report_repo: DailyReportRepository = Depends(get_daily_report_repository),
    industry_repo: IndustryRepository = Depends(get_industry_repository),
    recall_repo: RecallRepositoryPort = Depends(get_recall_repository),
) -> DailyReportUseCase:
    return _compose_daily_report_interactor(report_repo, industry_repo, recall_repo)


def build_daily_report_use_case(session: AsyncSession) -> DailyReportUseCase:
    """Script/manual composition root (no FastAPI Depends)."""
    return _compose_daily_report_interactor(
        DailyReportPgRepository(session),
        IndustryPgRepository(session),
        RecallPgRepository(session),
    )


def build_report_scheduler_use_case(session: AsyncSession) -> ReportSchedulerUseCase:
    """Script/scheduler composition root (no FastAPI Depends)."""
    return ReportSchedulerInteractor(
        auth_repo=AuthPgRepository(session),
        industry_repo=IndustryPgRepository(session),
        daily_report_use_case=build_daily_report_use_case(session),
    )


def get_report_scheduler_use_case(
    auth_repo: AuthRepository = Depends(get_auth_repository),
    industry_repo: IndustryRepository = Depends(get_industry_repository),
    daily_report_use_case: DailyReportUseCase = Depends(get_daily_report_use_case),
) -> ReportSchedulerUseCase:
    return ReportSchedulerInteractor(
        auth_repo=auth_repo,
        industry_repo=industry_repo,
        daily_report_use_case=daily_report_use_case,
    )
