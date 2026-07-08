from typing import Protocol, List
from mfds_user.domain.entities.regulation_entity import Regulation
from mfds_user.domain.value_objects.report_section_vo import ReportItem

class RegulationApiPort(Protocol):
    async def search_regulations(self, query: str) -> List[Regulation]:
        """법제처 API를 통해 키워드로 법령 및 행정규칙을 검색합니다."""
        ...

    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        """일일 리포트용 법규 변동 데이터를 가져옵니다."""
        ...
