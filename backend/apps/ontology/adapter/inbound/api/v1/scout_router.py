from fastapi import APIRouter, Depends, HTTPException, status

from matrix.grid_admin_guard_manager import verify_admin_jwt

from ontology.adapter.inbound.api.schemas.scout_schema import (
    ScoutPlanSchema,
    ScoutResultsResponse,
    ScoutRunRequest,
    ScoutRunResponse,
)
from ontology.app.dtos.scout_dto import ScoutCommand
from ontology.app.ports.input.scout_results_use_case import IScoutResultsUseCase
from ontology.app.ports.input.scout_use_case import IScoutUseCase
from ontology.dependencies.scout_provider import get_scout_results_use_case, get_scout_use_case

router = APIRouter(prefix="/scout", tags=["scout"])


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "scout"}


@router.get("/results", response_model=ScoutResultsResponse)
async def results(
    kind: str = "crawled",
    limit: int = 200,
    use_case: IScoutResultsUseCase = Depends(get_scout_results_use_case),
    _admin: str = Depends(verify_admin_jwt),
) -> ScoutResultsResponse:
    try:
        view = await use_case.list(kind, limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ScoutResultsResponse(kind=view.kind, count=len(view.items), items=view.items)


@router.post("/run", response_model=ScoutRunResponse)
async def run(
    body: ScoutRunRequest,
    use_case: IScoutUseCase = Depends(get_scout_use_case),
    _admin: str = Depends(verify_admin_jwt),
) -> ScoutRunResponse:
    try:
        result = await use_case.run(
            ScoutCommand(mode=body.mode, url=body.url, command=body.command)
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ScoutRunResponse(
        mode=result.mode,
        plan=ScoutPlanSchema(
            max_pages=result.plan.max_pages,
            max_depth=result.plan.max_depth,
            max_items=result.plan.max_items,
            keywords=result.plan.keywords,
            reason=result.plan.reason,
        ),
        summary=result.summary,
    )
