from pydantic import BaseModel
from typing import Optional, List
from mfds_user.domain.value_objects.category_type_vo import CategoryType

class IndustryCategory(BaseModel):
    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    code: str
    type: CategoryType
    parent_code: Optional[str] = None
    depth: int = 1
    is_flat: bool = False
    name_ko: str
    crawler_param: Optional[str] = None
    keywords: List[str] = []
