from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import (
    ChatCommand,
    ChatResponse,
    SmithCaptainQuery,
    SmithCaptainResponse,
)


class SmithCaptainUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        """스미스 선장의 자기소개."""
        ...

    @abstractmethod
    async def chat(self, command: ChatCommand) -> ChatResponse:
        '''사용자 자연어 입력을 받아 채팅 응답을 반환'''
        pass
