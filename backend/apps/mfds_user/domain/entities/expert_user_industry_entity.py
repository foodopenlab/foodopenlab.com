from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ExpertUserIndustry(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    id: UUID
    expert_user_id: UUID
    category_code: str
    created_at: datetime
