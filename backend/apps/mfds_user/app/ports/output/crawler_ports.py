from typing import Protocol, List, Dict
from mfds_user.domain.value_objects.report_section_vo import ReportItem

class ThinkfoodPort(Protocol):
    async def fetch(self, section_codes: List[str]) -> List[ReportItem]:
        ...

class MfdsPressPort(Protocol):
    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        ...

class RecallReportPort(Protocol):
    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        ...

class RegulationReportPort(Protocol):
    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        ...

class FoodRiskPort(Protocol):
    async def fetch(self, keywords: List[str]) -> Dict:
        ...

class ResearchPort(Protocol):
    async def fetch(self, keywords: List[str], days_back: int = 30) -> List[ReportItem]:
        ...

class FoodStatsPort(Protocol):
    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        ...
