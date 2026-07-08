from fastapi import APIRouter, Depends, HTTPException, status

from braindead.adapter.inbound.api.schemas.email_schema import SendEmailRequest, SendEmailResponse
from braindead.app.dtos.email_dto import SendEmailCommand
from braindead.app.ports.input.email_use_case import IEmailUseCase
from braindead.dependencies.email_provider import get_email_use_case
from matrix.grid_admin_guard_manager import verify_admin_jwt

router = APIRouter(tags=["braindead"])


@router.post("/braindead/send-email", response_model=SendEmailResponse, dependencies=[Depends(verify_admin_jwt)])
async def send_email(
    req: SendEmailRequest,
    use_case: IEmailUseCase = Depends(get_email_use_case),
) -> SendEmailResponse:
    result = await use_case.send_email(SendEmailCommand(to=req.to, prompt=req.prompt, to_name=req.to_name))
    if not result.success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=result.message)
    return SendEmailResponse(success=result.success, message=result.message)
