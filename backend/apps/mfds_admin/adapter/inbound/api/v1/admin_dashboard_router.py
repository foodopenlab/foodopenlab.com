from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, Optional
from mfds_admin.app.ports.input.logs_use_case import LogsUseCase
from mfds_admin.dependencies.logs import get_logs_use_case
from mfds_admin.adapter.inbound.api.middlewares.admin_auth_middleware import verify_admin_token
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import AdminTokenPayloadSchema
from mfds_admin.adapter.inbound.api.schemas.logs_schema import (
    ApiLogListResponse,
    SearchLogListResponse,
    DashboardResponse,
    AdminApiStatsSchema,
    ApiLogItemSchema,
    SearchLogItemSchema,
    UsersBlockSchema,
    ChatsBlockSchema,
    ApiBlockSchema,
    AdminApiStatItemSchema
)

router = APIRouter(tags=["admin"])

@router.get("/admin/logs/api", response_model=ApiLogListResponse)
async def list_api_logs(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    api_name: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    use_case: LogsUseCase = Depends(get_logs_use_case)
) -> ApiLogListResponse:
    try:
        items, total = await use_case.list_api_logs(page, size, api_name)
        return ApiLogListResponse(
            total=total,
            page=page,
            items=[
                ApiLogItemSchema(
                    id=x.id,
                    api_name=x.api_name,
                    endpoint=x.endpoint,
                    status_code=x.status_code,
                    response_ms=x.response_ms,
                    is_cache_hit=x.is_cache_hit,
                    called_at=x.called_at
                )
                for x in items
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/admin/logs/search", response_model=SearchLogListResponse)
async def list_search_logs(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    query_pattern: Optional[str] = None,
    page: int = 1,
    size: int = 50,
    use_case: LogsUseCase = Depends(get_logs_use_case)
) -> SearchLogListResponse:
    try:
        items, total = await use_case.list_search_logs(page, size, query_pattern)
        return SearchLogListResponse(
            total=total,
            page=page,
            items=[
                SearchLogItemSchema(
                    id=x.id,
                    actor_type=x.actor_type,
                    actor_id=x.actor_id,
                    keyword=x.keyword,
                    query_pattern=x.query_pattern,
                    searched_at=x.searched_at
                )
                for x in items
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/admin/dashboard", response_model=DashboardResponse)
async def admin_dashboard(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: LogsUseCase = Depends(get_logs_use_case)
) -> DashboardResponse:
    try:
        res = await use_case.get_dashboard_stats()
        users_data = res["users"]
        chats_data = res["chats"]
        api_data = res["api"]
        return DashboardResponse(
            users=UsersBlockSchema(
                total=users_data["total"],
                active=users_data["active"],
            ),
            chats=ChatsBlockSchema(
                today_total=chats_data["today_total"],
                analysis_total=chats_data["analysis_total"],
                regulation_total=chats_data["regulation_total"],
                ingredient_total=chats_data["ingredient_total"]
            ),
            api=ApiBlockSchema(
                today_calls=api_data["today_calls"],
                today_errors=api_data["today_errors"],
                top_api=api_data["top_api"]
            )
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/admin/api-stats", response_model=AdminApiStatsSchema)
async def admin_api_stats(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    period: str = "today",
    use_case: LogsUseCase = Depends(get_logs_use_case)
) -> AdminApiStatsSchema:
    try:
        res = await use_case.get_api_stats(period)
        return AdminApiStatsSchema(
            period=res["period"],
            stats=[
                AdminApiStatItemSchema(
                    api_name=x["api_name"],
                    total_calls=x["total_calls"],
                    cache_hits=x["cache_hits"],
                    cache_hit_rate=x["cache_hit_rate"],
                    avg_response_ms=x["avg_response_ms"],
                    error_count=x["error_count"],
                    error_rate=x["error_rate"]
                )
                for x in res["stats"]
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
