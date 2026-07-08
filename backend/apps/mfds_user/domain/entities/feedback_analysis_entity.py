from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import List, Dict

class FeedbackAnalysis(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    id: UUID
    industry_code: str
    analyzed_at: datetime
    feedback_count: int
    period_start: date
    period_end: date
    missing_topics: List[str] = []
    improvement_keys: List[str] = []
    useful_sections: Dict[str, float] = {}
    summary: str
    action_items: List[str] = []
