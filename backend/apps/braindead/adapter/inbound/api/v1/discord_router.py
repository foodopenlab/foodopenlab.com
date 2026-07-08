from fastapi import APIRouter, Depends, HTTPException, status

from braindead.adapter.inbound.api.schemas.discord_schema import SendDiscordRequest, SendDiscordResponse
from braindead.app.dtos.discord_dto import SendDiscordCommand
from braindead.app.ports.input.discord_use_case import IDiscordUseCase
from braindead.dependencies.discord_provider import get_discord_use_case
from matrix.grid_admin_guard_manager import verify_admin_jwt

router = APIRouter(tags=["braindead"])


@router.post("/braindead/send-discord", response_model=SendDiscordResponse, dependencies=[Depends(verify_admin_jwt)])
async def send_discord(
    req: SendDiscordRequest,
    use_case: IDiscordUseCase = Depends(get_discord_use_case),
) -> SendDiscordResponse:
    result = await use_case.send(SendDiscordCommand(channel=req.channel, prompt=req.prompt))
    if not result.success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.message)
    return SendDiscordResponse(success=result.success, message=result.message)
