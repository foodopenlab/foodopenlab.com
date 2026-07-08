import logging
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status

from braindead.adapter.inbound.api.schemas.inbox_schema import InboxEmailResponse, ReceiveEmailRequest
from braindead.adapter.inbound.mappers.inbox_mapper import InboxMapper
from braindead.app.ports.input.inbox_use_case import IInboxUseCase
from braindead.app.ports.input.watcher_use_case import IWatcherUseCase
from braindead.dependencies.inbox_provider import get_inbox_use_case
from braindead.dependencies.watcher_provider import get_watcher_use_case
from matrix.grid_admin_guard_manager import verify_admin_jwt

logger = logging.getLogger(__name__)

router = APIRouter(tags=["braindead"])


def verify_webhook_secret(x_webhook_secret: str | None = Header(default=None)) -> None:
    expected = os.getenv("N8N_INBOX_WEBHOOK_SECRET")
    if not expected:
        logger.warning("N8N_INBOX_WEBHOOK_SECRET 미설정 — 인증 없이 /braindead/inbox/receive 요청을 허용합니다.")
        return
    if x_webhook_secret != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid webhook secret")


@router.post("/braindead/inbox/receive", response_model=InboxEmailResponse, dependencies=[Depends(verify_webhook_secret)])
async def receive_email(
    req: ReceiveEmailRequest,
    inbox_use_case: IInboxUseCase = Depends(get_inbox_use_case),
    watcher_use_case: IWatcherUseCase = Depends(get_watcher_use_case),
) -> InboxEmailResponse:
    # Watson(KcELECTRA) 필터 — 차단 판정이면 저장·임베딩 없이 드롭
    filter_result = await watcher_use_case.filter_email(f"{req.subject}\n{req.body}")
    if not filter_result.is_normal:
        logger.info(
            "[inbox_router] 차단된 메일 드롭 | from=%s subject=%s label=%s",
            req.from_email, req.subject, filter_result.label,
        )
        return InboxEmailResponse(
            id=None,
            gmail_message_id=req.gmail_message_id,
            from_email=req.from_email,
            from_name=req.from_name,
            subject=req.subject,
            body=req.body,
            received_at=req.received_at,
            filtered=True,
        )

    cmd = InboxMapper.to_command(req)
    result = await inbox_use_case.receive(cmd)
    return InboxMapper.to_response(result)


@router.get("/braindead/inbox", response_model=list[InboxEmailResponse], dependencies=[Depends(verify_admin_jwt)])
async def list_inbox(
    use_case: IInboxUseCase = Depends(get_inbox_use_case),
) -> list[InboxEmailResponse]:
    dtos = await use_case.list_all()
    return [InboxMapper.to_response(dto) for dto in dtos]
