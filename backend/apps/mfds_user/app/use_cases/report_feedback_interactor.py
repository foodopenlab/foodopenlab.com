from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date

from mfds_user.app.ports.input.report_feedback_use_case import ReportFeedbackUseCase
from mfds_user.app.ports.output.report_feedback_repository import ReportFeedbackRepository, FeedbackAnalysisLLMPort
from mfds_user.app.ports.output.daily_report_repository import DailyReportRepository
from mfds_user.domain.entities.report_feedback_entity import ReportFeedback
from mfds_user.domain.entities.feedback_analysis_entity import FeedbackAnalysis
from mfds_user.domain.value_objects.report_section_vo import SectionType

class ReportFeedbackInteractor(ReportFeedbackUseCase):
    def __init__(
        self,
        feedback_repo: ReportFeedbackRepository,
        report_repo: DailyReportRepository,
        llm_port: FeedbackAnalysisLLMPort
    ) -> None:
        self.feedback_repo = feedback_repo
        self.report_repo = report_repo
        self.llm_port = llm_port

    async def submit_feedback(
        self,
        expert_user_id: UUID,
        report_id: UUID,
        useful_sections: List[SectionType],
        content_feedback: Optional[str],
        missing_feedback: Optional[str],
        improvement_feedback: Optional[str],
        usefulness_score: int
    ) -> ReportFeedback:
        # 1. Verify report existence and user ownership
        report = await self.report_repo.find(report_id)
        if not report:
            raise ValueError("리포트를 찾을 수 없습니다.")
        if report.expert_user_id != expert_user_id:
            raise PermissionError("해당 리포트에 대한 피드백 작성 권한이 없습니다.")

        # 2. Check duplicate submission
        existing = await self.feedback_repo.find_by_report_and_user(report_id, expert_user_id)
        if existing:
            raise ValueError("이미 해당 리포트에 피드백을 제출했습니다.")

        # 3. Domain validation
        feedback = ReportFeedback(
            id=uuid4(),
            report_id=report_id,
            expert_user_id=expert_user_id,
            created_at=datetime.utcnow(),
            useful_sections=useful_sections,
            content_feedback=content_feedback,
            missing_feedback=missing_feedback,
            improvement_feedback=improvement_feedback,
            usefulness_score=usefulness_score
        )
        if not feedback.is_valid():
            raise ValueError("점수(1~5)와 최소 1개 이상의 서술형 피드백을 작성해 주세요.")

        return await self.feedback_repo.save(feedback)

    async def get_feedback(self, expert_user_id: UUID, report_id: UUID) -> Optional[ReportFeedback]:
        return await self.feedback_repo.find_by_report_and_user(report_id, expert_user_id)

    async def get_feedback_analysis(self, industry_code: Optional[str] = None) -> List[FeedbackAnalysis]:
        return await self.feedback_repo.find_all_analysis(industry_code)

    async def analyze_feedback(self, industry_code: str, period_start: date, period_end: date) -> FeedbackAnalysis:
        feedbacks = await self.feedback_repo.find_by_industry_period(industry_code, period_start, period_end)
        if len(feedbacks) < 5:
            raise ValueError(f"분석에 최소 5건의 피드백이 필요합니다. (현재 {len(feedbacks)}건)")

        result = await self.llm_port.analyze(feedbacks, industry_code, period_start, period_end)

        analysis = FeedbackAnalysis(
            id=uuid4(),
            industry_code=industry_code,
            analyzed_at=datetime.utcnow(),
            feedback_count=len(feedbacks),
            period_start=period_start,
            period_end=period_end,
            missing_topics=result.get("missing_topics", []),
            improvement_keys=result.get("improvement_keys", []),
            useful_sections=result.get("useful_sections", {}),
            summary=result.get("summary", ""),
            action_items=result.get("action_items", [])
        )
        return await self.feedback_repo.save_analysis(analysis)
