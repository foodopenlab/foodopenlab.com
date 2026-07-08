from typing import Protocol, List
from datetime import date
from mfds_user.domain.value_objects.report_section_vo import ReportSection
from mfds_user.domain.value_objects.industry_filter_vo import IndustryFilter

class ReportLLMPort(Protocol):
    async def generate_summary(
        self,
        sections: List[ReportSection],
        industry_filter: IndustryFilter,
        report_date: date,
    ) -> str:
        """수집된 섹션 데이터를 HTML 형식으로 포맷팅된 요약 본문으로 변환합니다."""
        ...
