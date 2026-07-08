from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel
from mfds_user.app.ports.input.chat_use_case import ChatUseCase
from mfds_user.dependencies.chat import get_chat_use_case
from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from mfds_user.adapter.inbound.api.schemas.chat_schema import (
    ChatRequestSchema,
    ChatResponseSchema,
    ChatPersistRequestSchema,
    ChatMessageFeedbackRequest,
    ChatMessageFeedbackResponse,
    ChatFeedbackStatsResponse,
    ChatFeedbackTrainingCandidate
)
from mfds_user.app.dtos.chat_dto import ChatPersistDTO, ChatRequestDTO, ChatHistoryItem

router = APIRouter(tags=["chat"])

# v9 new satisfaction request schemas
class SatisfactionRequest(BaseModel):
    is_positive: bool

class ExpertFeedbackRequest(BaseModel):
    label: str
    memo: Optional[str] = None

@router.post("/chat/persist-exchange", response_model=ChatResponseSchema)
async def persist_chat_exchange(
    req: ChatPersistRequestSchema,
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponseSchema:
    dto = ChatPersistDTO(
        session_key=req.session_key,
        user_message=req.user_message,
        assistant_message=req.assistant_message,
        query_pattern=req.query_pattern or "law",
    )
    res_dto = await use_case.persist_exchange(dto)
    return ChatResponseSchema(
        reply=res_dto.reply,
        session_key=res_dto.session_key,
        message_id=res_dto.message_id,
    )

@router.post("/analysis-chat", response_model=ChatResponseSchema)
async def analysis_chat(
    req: ChatRequestSchema,
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> ChatResponseSchema:
    actor_id = None
    actor_type = None
    if req.user_id:
        try:
            actor_id = UUID(req.user_id)
            actor_type = "expert"
        except ValueError:
            pass

    history = [ChatHistoryItem(role=h.role, content=h.content) for h in req.history]
    dto = ChatRequestDTO(
        session_key=req.session_key,
        message=req.message,
        history=history,
        actor_id=actor_id,
        actor_type=actor_type
    )

    res_dto = await use_case.handle_chat(dto)
    return ChatResponseSchema(
        reply=res_dto.reply,
        session_key=res_dto.session_key,
        message_id=res_dto.message_id
    )

# --- Legacy Compatibility Feedback API ---
@router.post("/chat/messages/{message_id}/feedback", response_model=ChatMessageFeedbackResponse)
async def upsert_chat_feedback(
    message_id: UUID,
    req: ChatMessageFeedbackRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> ChatMessageFeedbackResponse:
    await use_case.save_legacy_feedback(
        message_id=message_id,
        session_key=req.session_key,
        accuracy_score=req.accuracy_score,
        relevance_score=req.relevance_score
    )
    return ChatMessageFeedbackResponse(
        message_id=message_id,
        session_key=req.session_key,
        accuracy_score=req.accuracy_score,
        relevance_score=req.relevance_score,
        comment=req.comment
    )

@router.get("/chat/messages/{message_id}/feedback", response_model=Optional[ChatMessageFeedbackResponse])
async def get_chat_feedback(
    message_id: UUID,
    session_key: str = Query(...),
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> Optional[ChatMessageFeedbackResponse]:
    fb = await use_case.get_legacy_feedback(message_id, session_key)
    if not fb:
        return None
    return ChatMessageFeedbackResponse(
        message_id=message_id,
        session_key=session_key,
        accuracy_score=fb["accuracy_score"],
        relevance_score=fb["relevance_score"],
        comment=None
    )

@router.get("/chat/feedback/stats", response_model=List[ChatFeedbackStatsResponse])
async def chat_feedback_stats(
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> List[ChatFeedbackStatsResponse]:
    stats = await use_case.get_feedback_stats()
    return [
        ChatFeedbackStatsResponse(
            chat_type=item["chat_type"],
            total_count=item["total_count"],
            avg_accuracy_score=item["avg_accuracy_score"],
            avg_relevance_score=item["avg_relevance_score"]
        ) for item in stats
    ]

@router.get("/chat/feedback/training-candidates", response_model=List[ChatFeedbackTrainingCandidate])
async def chat_feedback_candidates(
    limit: int = 100,
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> List[ChatFeedbackTrainingCandidate]:
    candidates = await use_case.get_low_score_candidates(limit)
    return [
        ChatFeedbackTrainingCandidate(
            feedback_id=item["feedback_id"],
            message_id=item["message_id"],
            room_id=item["room_id"],
            chat_type=item["chat_type"],
            accuracy_score=item["accuracy_score"],
            relevance_score=item["relevance_score"],
            question=item["question"],
            answer=item["answer"],
            comment=item["comment"],
            created_at=item["created_at"]
        ) for item in candidates
    ]

# --- v9 Clean Feedback APIs ---
@router.post("/messages/{message_id}/feedback/satisfaction", status_code=status.HTTP_201_CREATED)
async def submit_satisfaction_feedback(
    message_id: UUID,
    req: SatisfactionRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> dict:
    await use_case.save_satisfaction_feedback(message_id, req.is_positive)
    return {"message": "만족도 평가가 제출되었습니다."}

@router.post("/messages/{message_id}/feedback/expert", status_code=status.HTTP_201_CREATED)
async def submit_expert_feedback(
    message_id: UUID,
    req: ExpertFeedbackRequest,
    current_user: UserTokenPayload = Depends(verify_token),
    use_case: ChatUseCase = Depends(get_chat_use_case)
) -> dict:
    try:
        expert_uuid = UUID(current_user.sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 전문가 식별자입니다."
        )

    try:
        await use_case.save_expert_feedback(
            message_id=message_id,
            expert_user_id=expert_uuid,
            label=req.label,
            memo=req.memo
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return {"message": "전문가 검증 평가가 제출되었습니다."}
