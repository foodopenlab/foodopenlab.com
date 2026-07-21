from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse


class AndrewsArchitectUseCase(ABC):

    @abstractmethod
    def analyze_intent(self, question: str) -> dict[str, Any]:
        '''Kiwi 형태소 분석으로 프론트 질문의 의도를 파악하는 추상 메소드'''
        pass

    @abstractmethod
    async def respond(self, message: str, context: str | None = None) -> str:
        '''Ollama로 자연어 응답 생성'''
        pass

    @abstractmethod
    async def compose_chat_reply(
        self,
        message: str,
        *,
        train_set: pd.DataFrame,
        train_stats: dict[str, Any],
        trained: dict[str, Any],
        scores: dict[str, Any],
    ) -> str:
        '''의도·crew 결과를 바탕으로 채팅 응답 문장 생성'''
        pass

    @abstractmethod
    async def introduce_myself(self, query: AndrewsArchitectQuery) -> AndrewsArchitectResponse:
        '''앤드류 아키텍트의 자기소개 메소드'''
        pass