from pydantic import BaseModel
from typing import Optional, List
from mfds_user.domain.entities.regulation_entity import Regulation

class RegulationSearchQuery(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_key: Optional[str] = None

class RegulationSearchResponse(BaseModel):
    items: List[Regulation]
    total: int
