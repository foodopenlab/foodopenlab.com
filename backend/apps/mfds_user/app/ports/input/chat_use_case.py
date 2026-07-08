from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID
from mfds_user.app.dtos.chat_dto import ChatPersistDTO, ChatRequestDTO, ChatResponseDTO

class ChatUseCase(ABC):
    @abstractmethod
    async def handle_chat(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """사용자의 질문을 분석하고, AI 답변을 생성하여 저장"""
        pass

    @abstractmethod
    async def persist_exchange(self, request: ChatPersistDTO) -> ChatResponseDTO:
        """이미 생성된 질문·답변 쌍을 저장하고 assistant message_id를 반환"""
        pass

    @abstractmethod
    async def save_legacy_feedback(self, message_id: UUID, session_key: str, accuracy_score: int, relevance_score: int) -> None:
        """기존 프론트엔드 호환용 피드백 저장"""
        pass

    @abstractmethod
    async def get_legacy_feedback(self, message_id: UUID, session_key: str) -> Optional[dict]:
        """기존 프론트엔드 호환용 피드백 조회"""
        pass

    @abstractmethod
    async def save_satisfaction_feedback(self, message_id: UUID, is_positive: bool) -> None:
        """추천/비추천 피드백 저장 (v9)"""
        pass

    @abstractmethod
    async def save_expert_feedback(self, message_id: UUID, expert_user_id: UUID, label: str, memo: Optional[str]) -> None:
        """전문가 라벨링 피드백 저장 (v9)"""
        pass

    @abstractmethod
    async def get_feedback_stats(self) -> list[dict]:
        """피드백 통계 조회"""
        pass

    @abstractmethod
    async def get_low_score_candidates(self, limit: int = 100) -> list[dict]:
        """오답 학습 후보군 조회"""
        pass
