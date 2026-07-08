from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import List

class SectionType(str, Enum):
    NEWS     = "NEWS"
    RECALL   = "RECALL"
    LAW      = "LAW"
    MFDS     = "MFDS"
    RISK     = "RISK"
    RESEARCH = "RESEARCH"   # PubMed + ScienceON
    STATS    = "STATS"      # FIS newsletter

class ReportItem(BaseModel):
    title: str
    url: str
    source: str
    published_at: date

class ReportSection(BaseModel):
    type: SectionType
    items: List[ReportItem]
    is_empty: bool

    @property
    def empty_message(self) -> str:
        return "당일 특이사항 없음" if self.is_empty else ""
