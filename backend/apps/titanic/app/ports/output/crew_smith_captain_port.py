from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import ChatResponse, SmithCaptainQuery, SmithCaptainResponse


class SmithCaptainPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        """스미스 선장 자기소개."""
        ...

    @abstractmethod
    async def chat(self, message: str) -> ChatResponse:
        '''사용자 자연어 메시지를 받아 응답을 반환'''
        pass
