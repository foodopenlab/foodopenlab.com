from typing import Protocol
from mfds_user.app.dtos.regulation_dto import RegulationSearchQuery, RegulationSearchResponse

class RegulationUseCase(Protocol):
    async def search_regulations(self, query: RegulationSearchQuery) -> RegulationSearchResponse:
        """사용자가 질의한 검색어에 매칭되는 법령 리스트를 리턴합니다."""
        ...
