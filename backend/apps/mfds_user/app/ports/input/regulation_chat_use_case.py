from typing import Protocol

from mfds_user.app.dtos.regulation_chat_dto import RegulationChatQuery, RegulationChatResponse


class RegulationChatUseCase(Protocol):
    async def chat(self, query: RegulationChatQuery) -> RegulationChatResponse: ...
