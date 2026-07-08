from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessageSchema(BaseModel):
    role: str = Field(..., description="메시지 역할 (user | assistant)")
    content: str = Field(..., description="메시지 본문")


class ChatRequestSchema(BaseModel):
    session_key: str = Field(..., min_length=1, max_length=64, description="채팅 세션 키")
    message: str = Field(..., min_length=1, description="사용자 입력 메시지")
    history: List[ChatMessageSchema] = Field(default_factory=list, description="이전 대화 이력")
    user_id: Optional[str] = Field(default=None, description="users.id 참조 (선택)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_key": "sess_abc123",
                "message": "HACCP 인증 절차를 알려주세요",
                "history": [],
                "user_id": None,
            }
        }
    }


class ChatResponseSchema(BaseModel):
    reply: str = Field(..., description="에이전트 응답")
    session_key: str = Field(..., description="채팅 세션 키")
    message_id: Optional[str] = Field(default=None, description="저장된 메시지 ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reply": "HACCP 인증은 ...",
                "session_key": "sess_abc123",
                "message_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }
    }


class ChatPersistRequestSchema(BaseModel):
    session_key: str = Field(..., min_length=1, max_length=64, description="채팅 세션 키")
    user_message: str = Field(..., min_length=1, description="사용자 메시지")
    assistant_message: str = Field(..., min_length=1, description="어시스턴트 응답")
    query_pattern: Optional[str] = Field(default="law", description="질의 패턴 분류")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_key": "sess_abc123",
                "user_message": "회수 기준은?",
                "assistant_message": "식품회수·판매중지 기준은 ...",
                "query_pattern": "law",
            }
        }
    }


class ChatMessageFeedbackRequest(BaseModel):
    session_key: str = Field(..., description="채팅 세션 키")
    accuracy_score: int = Field(..., description="정확도 점수")
    relevance_score: int = Field(..., description="관련성 점수")
    user_id: Optional[str] = Field(default=None, description="사용자 UUID (선택)")
    comment: Optional[str] = Field(default=None, description="추가 코멘트")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_key": "sess_abc123",
                "accuracy_score": 4,
                "relevance_score": 5,
                "user_id": None,
                "comment": "출처가 명확했습니다",
            }
        }
    }


class ChatMessageFeedbackResponse(BaseModel):
    message_id: UUID = Field(..., description="피드백 대상 메시지 ID")
    session_key: str = Field(..., description="채팅 세션 키")
    accuracy_score: int = Field(..., description="정확도 점수")
    relevance_score: int = Field(..., description="관련성 점수")
    comment: Optional[str] = Field(default=None, description="추가 코멘트")


class ChatFeedbackStatsResponse(BaseModel):
    chat_type: str = Field(..., description="채팅 유형")
    total_count: int = Field(..., description="피드백 건수")
    avg_accuracy_score: float = Field(..., description="평균 정확도")
    avg_relevance_score: float = Field(..., description="평균 관련성")


class ChatFeedbackTrainingCandidate(BaseModel):
    feedback_id: str = Field(..., description="피드백 ID")
    message_id: str = Field(..., description="메시지 ID")
    room_id: str = Field(..., description="채팅방 ID")
    chat_type: str = Field(..., description="채팅 유형")
    accuracy_score: int = Field(..., description="정확도 점수")
    relevance_score: int = Field(..., description="관련성 점수")
    question: Optional[str] = Field(default=None, description="사용자 질문")
    answer: str = Field(..., description="어시스턴트 답변")
    comment: Optional[str] = Field(default=None, description="추가 코멘트")
    created_at: datetime = Field(..., description="피드백 생성 시각")
