from typing import Protocol

class ReportSchedulerUseCase(Protocol):
    async def generate_all(self) -> dict:
        """모든 활성 전문가회원에 대해 일일 리포트 배치를 수행합니다."""
        ...
