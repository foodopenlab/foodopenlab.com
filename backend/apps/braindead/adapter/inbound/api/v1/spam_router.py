from fastapi import APIRouter, Depends

from braindead.adapter.inbound.api.schemas.spam_schema import SpamCheckRequest, SpamCheckResponse
from braindead.adapter.inbound.mappers.spam_mapper import SpamMapper
from braindead.app.ports.input.spam_use_case import ISpamUseCase
from braindead.dependencies.spam_provider import get_spam_use_case

router = APIRouter(tags=["braindead"])


@router.post("/braindead/spam/check", response_model=SpamCheckResponse)
async def check_spam(
    req: SpamCheckRequest,
    use_case: ISpamUseCase = Depends(get_spam_use_case),
) -> SpamCheckResponse:
    cmd = SpamMapper.to_command(req.message)
    result = await use_case.check(cmd)
    return SpamMapper.to_response(result)


@router.get("/braindead/spam/history", response_model=list[SpamCheckResponse])
async def spam_history(
    use_case: ISpamUseCase = Depends(get_spam_use_case),
) -> list[SpamCheckResponse]:
    dtos = await use_case.history()
    return [SpamMapper.to_response(dto) for dto in dtos]
