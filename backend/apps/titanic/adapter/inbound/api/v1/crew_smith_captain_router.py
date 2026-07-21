import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema
from titanic.app.dtos.crew_smith_captain_dto import (
    ChatCommand,
    ChatMessage,
    ChatResponse,
    SmithCaptainQuery,
    SmithCaptainResponse,
)
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.dependencies.crew_smith_captain_provider import get_smith_captain_use_case

logger = logging.getLogger(__name__)

'''
스미스 선장 (Captain Edward John Smith)
타이타닉의 총책임자. 침몰하는 배와 운명을 함께한 명장.
전체 승객 현황(생존/사망 통계)을 관장하는 마스터 역할.

추천 파일명: smith_captain_router.py (또는 smith_wheel_router.py)
'''

smith_captain_router = APIRouter(prefix="/smith", tags=["smith"])


@smith_captain_router.post("/chat")
async def chat(
    schema: Annotated[ChatSchema, Body()],
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case)
) -> ChatResponse:
    for msg in schema.messages:
        logger.info("[smith/chat] messages | role=%s | text=%s", msg.role, msg.text)
    command = ChatCommand(
        messages=[ChatMessage(role=m.role, text=m.text) for m in schema.messages],
        system_instruction=schema.systemInstruction,
    )
    return await smith.chat(command)

@smith_captain_router.get("/myself")
async def introduce_myself(
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case)
) -> SmithCaptainResponse :
    return await smith.introduce_myself(SmithCaptainQuery(
            id=7,
            name="스미스 선장 (Captain Edward John Smith)"
        )
    )