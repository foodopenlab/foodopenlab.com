from fastapi import APIRouter, Depends

from braindead.adapter.inbound.api.schemas.judge_schema import JudgeSchema
from braindead.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from braindead.app.ports.input.judge_use_case import IJudgeUseCase
from braindead.dependencies.judge_provider import get_judge_use_case

router = APIRouter(tags=["braindead"])


@router.get("/judge/myself", response_model=JudgeSchema)
async def introduce_myself(
    use_case: IJudgeUseCase = Depends(get_judge_use_case),
) -> JudgeResponse:
    return await use_case.introduce_myself(JudgeQuery(id=0, name="Judge"))
