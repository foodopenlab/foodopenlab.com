from fastapi import APIRouter, Depends

from braindead.adapter.inbound.api.schemas.watcher_schema import (
    FilterCheckRequest,
    FilterCheckResponse,
    WatcherSchema,
)
from braindead.app.dtos.watcher_dto import WatcherResponse
from braindead.app.ports.input.watcher_use_case import IWatcherUseCase
from braindead.dependencies.watcher_provider import get_watcher_use_case

router = APIRouter(tags=["braindead"])


@router.get("/watcher/myself", response_model=WatcherSchema)
async def introduce_myself(
    use_case: IWatcherUseCase = Depends(get_watcher_use_case),
) -> WatcherResponse:
    return await use_case.introduce_myself(WatcherSchema(id=0, name="Watcher"))


@router.post("/watcher/filter", response_model=FilterCheckResponse)
async def filter_email(
    req: FilterCheckRequest,
    use_case: IWatcherUseCase = Depends(get_watcher_use_case),
) -> FilterCheckResponse:
    result = await use_case.filter_email(req.text)
    return FilterCheckResponse(label=result.label, is_normal=result.is_normal)
