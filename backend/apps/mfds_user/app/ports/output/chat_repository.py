from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from mfds_user.domain.entities.agent_message_entity import AgentMessage

class ChatRepository(ABC):
    @abstractmethod
    async def find_session(self, session_id: UUID) -> Optional[dict]:
        """세션 조회"""
        pass

    @abstractmethod
    async def create_session(self, session_id: UUID, actor_type: str, actor_id: UUID) -> dict:
        """세션 생성"""
        pass

    @abstractmethod
    async def update_session_active(self, session_id: UUID) -> None:
        """세션 활성화 시각 갱신"""
        pass

    @abstractmethod
    async def save_message(self, message: AgentMessage) -> AgentMessage:
        """메시지 저장"""
        pass

    @abstractmethod
    async def find_messages_by_session(self, session_id: UUID) -> list[AgentMessage]:
        """세션의 이전 대화 목록 조회"""
        pass

    @abstractmethod
    async def save_satisfaction_feedback(self, message_id: UUID, is_positive: bool) -> None:
        """만족도 피드백 저장"""
        pass

    @abstractmethod
    async def find_satisfaction_feedback(self, message_id: UUID) -> Optional[bool]:
        """만족도 피드백 여부 조회"""
        pass

    @abstractmethod
    async def save_expert_feedback(self, message_id: UUID, expert_user_id: UUID, label: str, memo: Optional[str]) -> None:
        """전문가 피드백 저장"""
        pass

    @abstractmethod
    async def find_expert_feedback(self, message_id: UUID) -> Optional[dict]:
        """전문가 피드백 조회"""
        pass

    @abstractmethod
    async def find_feedback_stats(self) -> list[dict]:
        """피드백 통계 조회"""
        pass

    @abstractmethod
    async def find_low_score_candidates(self, limit: int) -> list[dict]:
        """낮은 점수의 피드백 후보군 조회"""
        pass
