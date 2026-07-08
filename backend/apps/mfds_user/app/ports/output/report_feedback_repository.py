from typing import Protocol, List, Optional, Dict
from uuid import UUID
from datetime import date
from mfds_user.domain.entities.report_feedback_entity import ReportFeedback
from mfds_user.domain.entities.feedback_analysis_entity import FeedbackAnalysis

class ReportFeedbackRepository(Protocol):
    async def find_by_report_and_user(self, report_id: UUID, expert_user_id: UUID) -> Optional[ReportFeedback]:
        ...

    async def save(self, feedback: ReportFeedback) -> ReportFeedback:
        ...

    async def find_by_industry_period(self, industry_code: str, period_start: date, period_end: date) -> List[ReportFeedback]:
        ...

    async def find_all_analysis(self, industry_code: Optional[str] = None) -> List[FeedbackAnalysis]:
        ...

    async def save_analysis(self, analysis: FeedbackAnalysis) -> FeedbackAnalysis:
        ...

class FeedbackAnalysisLLMPort(Protocol):
    async def analyze(
        self,
        feedbacks: List[ReportFeedback],
        industry_code: str,
        period_start: date,
        period_end: date
    ) -> Dict:
        """전문가 피드백 데이터를 분석하여 missing_topics, improvement_keys, useful_sections, summary, action_items를 추출합니다."""
        ...
