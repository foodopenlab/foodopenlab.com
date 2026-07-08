from mfds_user.app.ports.input.regulation_use_case import RegulationUseCase
from mfds_user.app.ports.output.regulation_api_port import RegulationApiPort
from mfds_user.app.dtos.regulation_dto import RegulationSearchQuery, RegulationSearchResponse

class RegulationInteractor(RegulationUseCase):
    def __init__(self, regulation_api_adapter: RegulationApiPort) -> None:
        self.regulation_api_adapter = regulation_api_adapter

    async def search_regulations(self, query: RegulationSearchQuery) -> RegulationSearchResponse:
        items = await self.regulation_api_adapter.search_regulations(query.query)
        return RegulationSearchResponse(
            items=items,
            total=len(items)
        )
