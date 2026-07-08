from fastapi import APIRouter, Depends, HTTPException, status

from braindead.adapter.inbound.api.schemas.telegram_schema import SendTelegramRequest, SendTelegramResponse
from braindead.app.dtos.telegram_dto import SendTelegramCommand
from braindead.app.ports.input.telegram_use_case import ITelegramUseCase
from braindead.dependencies.telegram_provider import get_telegram_use_case
from matrix.grid_admin_guard_manager import verify_admin_jwt

router = APIRouter(tags=["braindead"])


@router.post("/braindead/send-telegram", response_model=SendTelegramResponse, dependencies=[Depends(verify_admin_jwt)])
async def send_telegram(
    req: SendTelegramRequest,
    use_case: ITelegramUseCase = Depends(get_telegram_use_case),
) -> SendTelegramResponse:
    result = await use_case.send(SendTelegramCommand(to=req.to, prompt=req.prompt))
    if not result.success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.message)
    return SendTelegramResponse(success=result.success, message=result.message)
