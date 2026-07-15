from abc import ABC, abstractmethod

from ontology.app.dtos.gateway_dto import GatewayQuery, GatewayResult


class IGatewayUseCase(ABC):
    """Driving Port — 시맨틱 게이트웨이의 단일 진입점."""

    @abstractmethod
    async def ask(self, query: GatewayQuery) -> GatewayResult: ...
