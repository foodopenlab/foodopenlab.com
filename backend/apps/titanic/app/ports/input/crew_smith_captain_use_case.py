from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import ChatResponse, SmithCaptainResponse


class SmithCaptainUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        """스미스 선장의 자기소개."""
        ...

    @abstractmethod
    async def chat(self, schema: ChatSchema) -> ChatResponse:
        '''사용자 자연어 입력을 받아 채팅 응답을 반환'''
        pass
