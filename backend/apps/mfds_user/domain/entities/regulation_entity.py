from pydantic import BaseModel
from datetime import date
from typing import Optional
from mfds_user.domain.value_objects.regulation_vo import LawType

class Regulation(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    law_id: str
    title: str
    law_type: LawType
    change_type: Optional[str] = None
    promulgation_date: Optional[date] = None
    promulgation_no: Optional[str] = None
    enforcement_date: Optional[date] = None
    source: Optional[str] = None
    url: str
