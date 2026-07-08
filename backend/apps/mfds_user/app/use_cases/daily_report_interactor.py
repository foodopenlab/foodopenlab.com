import asyncio
import re
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from uuid import UUID, uuid4

from mfds_user.app.ports.input.daily_report_use_case import DailyReportUseCase
from mfds_user.app.ports.output.daily_report_repository import DailyReportRepository
from mfds_user.app.ports.output.industry_repository import IndustryRepository
from mfds_user.app.ports.output.crawler_ports import (
    ThinkfoodPort,
    MfdsPressPort,
    RecallReportPort,
    RegulationReportPort,
    FoodRiskPort,
    ResearchPort,
    FoodStatsPort
)
from mfds_user.app.ports.output.report_llm_port import ReportLLMPort
from mfds_user.domain.entities.daily_report_entity import DailyReport
from mfds_user.domain.value_objects.report_section_vo import ReportSection, SectionType, ReportItem
from mfds_user.domain.value_objects.industry_filter_vo import IndustryFilter

SECTION_ITEM_LIMITS = {
    SectionType.NEWS:     10,
    SectionType.RECALL:    5,
    SectionType.LAW:       5,
    SectionType.MFDS:      5,
    SectionType.RISK:      1,
    SectionType.RESEARCH:  5,
    SectionType.STATS:     3,
}

EMPTY_REPORT_HTML = """
<article class="daily-report empty">
  <p class="empty-notice">오늘은 선택하신 업종 관련 특이사항이 없습니다.</p>
</article>
"""

def extract_preview(html: str, length: int = 150) -> str:
    plain = re.sub(r'<[^>]+>', '', html)
    # Replace multiple spaces/newlines
    plain = re.sub(r'\s+', ' ', plain)
    return plain[:length].strip()

class DailyReportInteractor(DailyReportUseCase):
    def __init__(
        self,
        report_repo: DailyReportRepository,
        industry_repo: IndustryRepository,
        thinkfood_port: ThinkfoodPort,
        mfds_port: MfdsPressPort,
        recall_port: RecallReportPort,
        regulation_port: RegulationReportPort,
        risk_port: FoodRiskPort,
        research_port: ResearchPort,
        stats_port: FoodStatsPort,
        llm_port: ReportLLMPort
    ) -> None:
        self.report_repo = report_repo
        self.industry_repo = industry_repo
        self.thinkfood_port = thinkfood_port
        self.mfds_port = mfds_port
        self.recall_port = recall_port
        self.regulation_port = regulation_port
        self.risk_port = risk_port
        self.research_port = research_port
        self.stats_port = stats_port
        self.llm_port = llm_port

    async def get_my_reports(self, expert_user_id: UUID) -> List[DailyReport]:
        await self.report_repo.delete_expired_unsaved(expert_user_id)
        return await self.report_repo.find_by_user(expert_user_id)

    async def get_report_detail(self, expert_user_id: UUID, report_id: UUID) -> DailyReport:
        report = await self.report_repo.find(report_id)
        if not report:
            raise ValueError("리포트를 찾을 수 없습니다.")
        if report.expert_user_id != expert_user_id:
            raise PermissionError("해당 리포트에 대한 접근 권한이 없습니다.")
        return report

    async def generate(self, expert_user_id: UUID) -> DailyReport:
        return await self.generate_for_date(expert_user_id, date.today(), force_refresh=False)

    async def generate_for_date(self, expert_user_id: UUID, report_date: date, force_refresh: bool = False) -> DailyReport:
        # 1. Check if already generated for the date
        existing = await self.report_repo.find_by_user_and_date(expert_user_id, report_date)
        if existing and not force_refresh:
            return existing
        if existing and force_refresh and not existing.is_saved:
            await self.report_repo.delete_by_user_and_date(expert_user_id, report_date)

        # 2. Get user selections & industry filter
        selections = await self.industry_repo.find_by_user(expert_user_id)
        if not selections:
            raise ValueError("선택된 업종 정보가 없습니다. 업종을 먼저 설정해 주세요.")

        selected_codes = [s.category_code for s in selections]
        categories = await self.industry_repo.find_by_codes(selected_codes)
        
        media_codes = []
        foodtype_mid_codes = []
        crawler_params = []
        keywords_set = set()

        for c in categories:
            if c.type == "media":
                media_codes.append(c.code)
                if c.crawler_param:
                    crawler_params.append(c.crawler_param)
            elif c.type == "foodtype":
                foodtype_mid_codes.append(c.code)
            
            # Collect all keywords
            for kw in c.keywords:
                keywords_set.add(kw)

        industry_filter = IndustryFilter(
            media_codes=media_codes,
            foodtype_mid_codes=foodtype_mid_codes,
            crawler_params=crawler_params,
            keywords=list(keywords_set)
        )

        # 3. Parallel fetch from all ports
        news_task = self.thinkfood_port.fetch(industry_filter.to_section_codes())
        recalls_task = self.recall_port.fetch(industry_filter.to_keywords())
        laws_task = self.regulation_port.fetch(industry_filter.to_keywords())
        mfds_task = self.mfds_port.fetch(industry_filter.to_keywords())
        risk_task = self.risk_port.fetch(industry_filter.to_keywords())
        research_task = self.research_port.fetch(industry_filter.to_keywords(), days_back=30)
        stats_task = self.stats_port.fetch(industry_filter.to_keywords())

        (news, recalls, laws, mfds, research, stats), risk = await asyncio.gather(
            asyncio.gather(news_task, recalls_task, laws_task, mfds_task, research_task, stats_task),
            risk_task,
        )

        # 4. Limit items & format sections
        def make_section(type_: SectionType, items_list: List[ReportItem]) -> ReportSection:
            limited = items_list[:SECTION_ITEM_LIMITS[type_]]
            return ReportSection(
                type=type_,
                items=limited,
                is_empty=len(limited) == 0
            )

        # Format risk as list of ReportItem if present
        risk_items = []
        if risk and risk.get("reason"):
            risk_items.append(ReportItem(
                title=f"식중독 위험현황: {risk.get('level', 'low')}",
                url="",
                source=f"위험지수: {risk.get('weather', '')}",
                published_at=report_date
            ))

        sections = [
            make_section(SectionType.NEWS,     news),
            make_section(SectionType.RECALL,   recalls),
            make_section(SectionType.LAW,      laws),
            make_section(SectionType.MFDS,     mfds),
            make_section(SectionType.RISK,     risk_items),
            make_section(SectionType.RESEARCH, research),
            make_section(SectionType.STATS,    stats),
        ]

        # 5. Handle empty report state
        all_empty = all(s.is_empty for s in sections)
        if all_empty:
            summary = EMPTY_REPORT_HTML
        else:
            # Call LLM to format/summarize HTML
            summary = await self.llm_port.generate_summary(sections, industry_filter, report_date)

        summary_preview = extract_preview(summary)

        # 6. Save report
        report = DailyReport(
            id=uuid4(),
            expert_user_id=expert_user_id,
            report_date=report_date,
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=7),
            is_saved=False,
            summary=summary,
            summary_preview=summary_preview,
            sections=sections
        )
        return await self.report_repo.save(report)

    async def save_report(self, expert_user_id: UUID, report_id: UUID) -> DailyReport:
        report = await self.report_repo.find(report_id)
        if not report:
            raise ValueError("리포트를 찾을 수 없습니다.")
        if report.expert_user_id != expert_user_id:
            raise PermissionError("해당 리포트에 대한 수정 권한이 없습니다.")
            
        report.is_saved = True
        return await self.report_repo.update(report)
