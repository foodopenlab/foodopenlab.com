from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from mfds_user.domain.value_objects.report_section_vo import SectionType

class ReportFeedback(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    id: UUID
    report_id: UUID
    expert_user_id: UUID
    created_at: datetime
    useful_sections: List[SectionType] = []
    content_feedback: Optional[str] = None
    missing_feedback: Optional[str] = None
    improvement_feedback: Optional[str] = None
    usefulness_score: int

    def is_valid(self) -> bool:
        return bool(
            self.usefulness_score and
            any([
                self.content_feedback,
                self.missing_feedback,
                self.improvement_feedback,
            ])
        )
