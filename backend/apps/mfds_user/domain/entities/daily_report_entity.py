from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import List
from mfds_user.domain.value_objects.report_section_vo import ReportSection

class DailyReport(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    id: UUID
    expert_user_id: UUID
    report_date: date
    generated_at: datetime
    expires_at: datetime
    is_saved: bool
    summary: str
    summary_preview: str
    sections: List[ReportSection]

    def is_expired(self) -> bool:
        return not self.is_saved and datetime.utcnow() > self.expires_at
