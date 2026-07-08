from typing import List, Optional
from uuid import UUID, uuid4
from datetime import date, datetime
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.app.ports.output.report_feedback_repository import ReportFeedbackRepository
from mfds_user.domain.entities.report_feedback_entity import ReportFeedback
from mfds_user.domain.entities.feedback_analysis_entity import FeedbackAnalysis
from mfds_user.domain.value_objects.report_section_vo import SectionType
from mfds_user.adapter.outbound.orm.report_feedback_orm import ReportFeedbackORM
from mfds_user.adapter.outbound.orm.report_feedback_sections_orm import ReportFeedbackSectionORM
from mfds_user.adapter.outbound.orm.report_feedback_analysis_orm import ReportFeedbackAnalysisORM
from mfds_user.adapter.outbound.orm.expert_user_industry_orm import ExpertUserIndustryORM

class ReportFeedbackPgRepository(ReportFeedbackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _to_entity(self, orm: ReportFeedbackORM) -> ReportFeedback:
        # Fetch sections
        stmt = select(ReportFeedbackSectionORM.section_type).where(
            ReportFeedbackSectionORM.feedback_id == orm.id
        )
        res = await self.session.execute(stmt)
        sections = [SectionType(s) for s in res.scalars().all()]

        return ReportFeedback(
            id=orm.id,
            report_id=orm.report_id,
            expert_user_id=orm.expert_user_id,
            created_at=orm.created_at,
            useful_sections=sections,
            content_feedback=orm.content_feedback,
            missing_feedback=orm.missing_feedback,
            improvement_feedback=orm.improvement_feedback,
            usefulness_score=orm.usefulness_score
        )

    async def find_by_report_and_user(self, report_id: UUID, expert_user_id: UUID) -> Optional[ReportFeedback]:
        stmt = select(ReportFeedbackORM).where(
            and_(
                ReportFeedbackORM.report_id == report_id,
                ReportFeedbackORM.expert_user_id == expert_user_id
            )
        )
        res = await self.session.execute(stmt)
        orm = res.scalar_one_or_none()
        if not orm:
            return None
        return await self._to_entity(orm)

    async def save(self, feedback: ReportFeedback) -> ReportFeedback:
        db_fb = ReportFeedbackORM(
            id=feedback.id,
            report_id=feedback.report_id,
            expert_user_id=feedback.expert_user_id,
            created_at=feedback.created_at,
            content_feedback=feedback.content_feedback,
            missing_feedback=feedback.missing_feedback,
            improvement_feedback=feedback.improvement_feedback,
            usefulness_score=feedback.usefulness_score
        )
        self.session.add(db_fb)

        # Save sections (1NF)
        for s in feedback.useful_sections:
            db_sec = ReportFeedbackSectionORM(
                id=uuid4(),
                feedback_id=feedback.id,
                section_type=s.value
            )
            self.session.add(db_sec)

        await self.session.commit()
        return feedback

    async def find_by_industry_period(
        self,
        industry_code: str,
        period_start: date,
        period_end: date
    ) -> List[ReportFeedback]:
        # Filter report feedbacks by joining with expert user industry
        # Since created_at is timestamp, convert dates to datetimes for range check
        start_dt = datetime.combine(period_start, datetime.min.time())
        end_dt = datetime.combine(period_end, datetime.max.time())
        
        stmt = select(ReportFeedbackORM).join(
            ExpertUserIndustryORM,
            ReportFeedbackORM.expert_user_id == ExpertUserIndustryORM.expert_user_id
        ).where(
            and_(
                ExpertUserIndustryORM.category_code == industry_code,
                ReportFeedbackORM.created_at >= start_dt,
                ReportFeedbackORM.created_at <= end_dt
            )
        ).distinct()

        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        
        entities = []
        for r in rows:
            entities.append(await self._to_entity(r))
        return entities

    async def find_all_analysis(self, industry_code: Optional[str] = None) -> List[FeedbackAnalysis]:
        stmt = select(ReportFeedbackAnalysisORM)
        if industry_code:
            stmt = stmt.where(ReportFeedbackAnalysisORM.industry_code == industry_code)
        stmt = stmt.order_by(ReportFeedbackAnalysisORM.analyzed_at.desc())
        
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        
        return [
            FeedbackAnalysis(
                id=r.id,
                industry_code=r.industry_code,
                analyzed_at=r.analyzed_at,
                feedback_count=r.feedback_count,
                period_start=r.period_start,
                period_end=r.period_end,
                missing_topics=r.missing_topics,
                improvement_keys=r.improvement_keys,
                useful_sections=r.useful_sections,
                summary=r.summary,
                action_items=r.action_items
            )
            for r in rows
        ]

    async def save_analysis(self, analysis: FeedbackAnalysis) -> FeedbackAnalysis:
        db_an = ReportFeedbackAnalysisORM(
            id=analysis.id,
            industry_code=analysis.industry_code,
            analyzed_at=analysis.analyzed_at,
            feedback_count=analysis.feedback_count,
            period_start=analysis.period_start,
            period_end=analysis.period_end,
            missing_topics=analysis.missing_topics,
            improvement_keys=analysis.improvement_keys,
            useful_sections=analysis.useful_sections,
            summary=analysis.summary,
            action_items=analysis.action_items
        )
        self.session.add(db_an)
        await self.session.commit()
        return analysis
