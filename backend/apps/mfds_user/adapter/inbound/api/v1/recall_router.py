from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from mfds_user.app.ports.input.recall_use_case import RecallUseCase
from mfds_user.app.ports.output.observability_ports import SearchLoggerPort
from mfds_user.dependencies.recall import get_recall_use_case
from mfds_user.dependencies.observability import get_search_logger
from mfds_user.adapter.inbound.api.schemas.recall_schema import (
    RecallSchema,
    RecallFoodTypesResponse,
    RecallListResponse,
    LatestRecallsResponse,
    RecallItemResponse
)
from mfds_user.app.dtos.recall_dto import RecallListQuery

router = APIRouter(prefix="", tags=["recalls"])

@router.get("/recalls/latest", response_model=LatestRecallsResponse)
async def get_latest_recalls(
    use_case: RecallUseCase = Depends(get_recall_use_case)
) -> LatestRecallsResponse:
    try:
        res = await use_case.latest_recalls()
        return LatestRecallsResponse(
            items=[RecallItemResponse(**item.__dict__) for item in res.items],
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

@router.get("/recalls", response_model=RecallListResponse)
async def recalls_list(
    food_category: str | None = None,
    food_type: str | None = None,
    grade: int | None = None,
    page: int = 1,
    size: int = 20,
    user_id: str | None = None,
    session_key: str | None = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    use_case: RecallUseCase = Depends(get_recall_use_case),
    search_logger: SearchLoggerPort = Depends(get_search_logger)
) -> RecallListResponse:
    query = RecallListQuery(
        food_category=food_category,
        food_type=food_type,
        grade=grade,
        page=page,
        size=size,
        user_id=int(user_id) if user_id and user_id.isdigit() else None,
        session_key=session_key
    )
    res = await use_case.list_recalls(query)

    # Log search in background via Port
    if food_category or food_type:
        kw = ", ".join(filter(None, [food_category, food_type]))
        background_tasks.add_task(
            search_logger.log_search,
            user_id,
            session_key,
            "recall",
            kw
        )

    # Map DTOs to Schemas
    items = [
        RecallSchema(
            id=item.id,
            product_name=item.product_name,
            manufacturer=item.manufacturer,
            food_type=item.food_type,
            food_category=item.food_category,
            recall_reason=item.recall_reason,
            recall_grade=item.recall_grade,
            recall_method=item.recall_method,
            registered_at=item.registered_at,
            image_url=item.image_url,
            prdlst_report_no=item.prdlst_report_no
        )
        for item in res.items
    ]

    return RecallListResponse(
        total=res.total,
        page=res.page,
        items=items,
        display_note=res.display_note
    )

@router.get("/recalls/food-types", response_model=RecallFoodTypesResponse)
async def recalls_food_types(
    use_case: RecallUseCase = Depends(get_recall_use_case)
) -> RecallFoodTypesResponse:
    types = await use_case.list_food_types()
    return RecallFoodTypesResponse(items=types)

@router.get("/recalls/{recall_id}", response_model=RecallSchema)
async def recalls_detail(
    recall_id: str,
    use_case: RecallUseCase = Depends(get_recall_use_case)
) -> RecallSchema:
    try:
        item = await use_case.get_recall_detail(recall_id)
        return RecallSchema(
            id=item.id,
            product_name=item.product_name,
            manufacturer=item.manufacturer,
            food_type=item.food_type,
            food_category=item.food_category,
            recall_reason=item.recall_reason,
            recall_grade=item.recall_grade,
            recall_method=item.recall_method,
            registered_at=item.registered_at,
            image_url=item.image_url,
            prdlst_report_no=item.prdlst_report_no
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
