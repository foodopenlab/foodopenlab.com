from typing import Protocol, List, Optional
from uuid import UUID
from datetime import date
from mfds_user.domain.entities.report_feedback_entity import ReportFeedback
from mfds_user.domain.entities.feedback_analysis_entity import FeedbackAnalysis
from mfds_user.domain.value_objects.report_section_vo import SectionType

class ReportFeedbackUseCase(Protocol):
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
        ...

    async def get_feedback(self, expert_user_id: UUID, report_id: UUID) -> Optional[ReportFeedback]:
        ...

    async def get_feedback_analysis(self, industry_code: Optional[str] = None) -> List[FeedbackAnalysis]:
        ...

    async def analyze_feedback(self, industry_code: str, period_start: date, period_end: date) -> FeedbackAnalysis:
        ...
