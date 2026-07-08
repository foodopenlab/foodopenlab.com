from fastapi import APIRouter, Depends, HTTPException, status

from mfds_user.adapter.inbound.api.schemas.regulation_chat_schema import (
    LawReferenceSchema,
    RegulationChatRequestSchema,
    RegulationChatResponseSchema,
)
from mfds_user.app.dtos.regulation_chat_dto import HistoryItem, RegulationChatQuery
from mfds_user.app.ports.input.regulation_chat_use_case import RegulationChatUseCase
from mfds_user.dependencies.regulation_chat import get_regulation_chat_use_case

router = APIRouter(prefix="/regulation-chat", tags=["regulation-chat"])


@router.post("", response_model=RegulationChatResponseSchema)
async def regulation_chat(
    body: RegulationChatRequestSchema,
    use_case: RegulationChatUseCase = Depends(get_regulation_chat_use_case),
) -> RegulationChatResponseSchema:
    if not body.message.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message가 필요합니다.")
    if not body.company_type.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="company_type이 필요합니다.")

    query = RegulationChatQuery(
        message=body.message.strip(),
        company_type=body.company_type.strip(),
        history=[HistoryItem(role=h.role, content=h.content) for h in body.history],
        session_key=body.session_key,
    )
    result = await use_case.chat(query)

    return RegulationChatResponseSchema(
        reply=result.reply,
        referenced_laws=[
            LawReferenceSchema(law_name=r.law_name, article=r.article)
            for r in result.referenced_laws
        ],
        session_key=result.session_key,
        message_id=None,
    )
