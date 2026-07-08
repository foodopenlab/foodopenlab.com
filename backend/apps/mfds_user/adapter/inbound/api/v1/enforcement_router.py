from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status

from mfds_user.app.ports.input.enforcement_use_case import EnforcementUseCase
from mfds_user.app.ports.output.observability_ports import SearchLoggerPort
from mfds_user.dependencies.enforcement import get_enforcement_use_case
from mfds_user.dependencies.observability import get_search_logger
from mfds_user.adapter.inbound.api.schemas.enforcement_schema import (
    EnforcementSchema,
    EnforcementListResponse,
    LatestSanctionsResponse,
    SanctionItemResponse
)
from mfds_user.app.dtos.enforcement_dto import EnforcementListQuery

router = APIRouter(prefix="", tags=["enforcement"])

@router.get("/sanctions/latest", response_model=LatestSanctionsResponse)
async def get_latest_sanctions(
    use_case: EnforcementUseCase = Depends(get_enforcement_use_case),
) -> LatestSanctionsResponse:
    try:
        res = await use_case.latest_sanctions()
        return LatestSanctionsResponse(
            items=[SanctionItemResponse(**item.__dict__) for item in res.items],
            fetched_at=res.fetched_at,
            query_date=res.query_date,
            is_today=res.is_today,
            matched_date=res.matched_date,
            last_sync_at=res.last_sync_at,
            sync_wave=res.sync_wave,
            sync_slot=res.sync_slot,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

@router.get("/enforcement", response_model=EnforcementListResponse)
async def enforcement_list(
    background_tasks: BackgroundTasks,
    use_case: EnforcementUseCase = Depends(get_enforcement_use_case),
    search_logger: SearchLoggerPort = Depends(get_search_logger),
    process_type: str | None = None,
    business_name: str | None = None,
    page: int = 1,
    size: int = 20,
    user_id: str | None = None,
    session_key: str | None = None,
) -> EnforcementListResponse:
    query = EnforcementListQuery(
        process_type=process_type,
        business_name=business_name,
        page=page,
        size=size,
        user_id=int(user_id) if user_id and user_id.isdigit() else None,
        session_key=session_key
    )
    res = await use_case.list_enforcements(query)

    # Log search in background via Port
    kw = ", ".join(filter(None, [(process_type or "").strip(), (business_name or "").strip()])) or "enforcement"
    background_tasks.add_task(
        search_logger.log_search,
        user_id,
        session_key,
        "enforcement",
        kw
    )

    # Map DTOs to Schemas
    items = [
        EnforcementSchema(
            id=item.id,
            business_name=item.business_name,
            business_type=item.business_type,
            address=item.address,
            process_type=item.process_type,
            violation_content=item.violation_content,
            violation_date=item.violation_date,
            process_date=item.process_date,
            district=item.district
        )
        for item in res.items
    ]

    return EnforcementListResponse(
        total=res.total,
        page=res.page,
        items=items,
        list_max=size,
        empty_label=res.empty_label,
        last_sync_at=res.last_sync_at,
        sync_wave=res.sync_wave,
        sync_slot=res.sync_slot
    )

@router.get("/enforcement/{enforcement_id}", response_model=EnforcementSchema)
async def enforcement_detail(
    enforcement_id: str,
    use_case: EnforcementUseCase = Depends(get_enforcement_use_case)
) -> EnforcementSchema:
    try:
        item = await use_case.get_enforcement_detail(enforcement_id)
        return EnforcementSchema(
            id=item.id,
            business_name=item.business_name,
            business_type=item.business_type,
            address=item.address,
            process_type=item.process_type,
            violation_content=item.violation_content,
            violation_date=item.violation_date,
            process_date=item.process_date,
            district=item.district
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
