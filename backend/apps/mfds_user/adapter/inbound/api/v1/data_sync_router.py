from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_admin_guard_manager import verify_admin_jwt
from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.cache.food_safety_sync_state import get_public_sync_state
from mfds_user.adapter.outbound.cache.recall_scheduler import trigger_manual_staggered_sync
from mfds_user.adapter.outbound.orm.enforcement_orm import EnforcementModel
from mfds_user.adapter.outbound.orm.recall_orm import RecallModel

router = APIRouter(prefix="/admin/data-sync", tags=["admin"], dependencies=[Depends(verify_admin_jwt)])


class DataSyncStatusResponse(BaseModel):
    recalls_db_count: int
    enforcements_db_count: int
    recall_cache_last_updated: str | None
    sanction_cache_last_updated: str | None
    last_sync_at: str | None
    sync_wave: str | None
    sync_slot: str | None


class DataSyncTriggerRequest(BaseModel):
    sync_type: str


class DataSyncTriggerResponse(BaseModel):
    started: bool
    message: str


@router.get("/status", response_model=DataSyncStatusResponse)
async def data_sync_status(db: AsyncSession = Depends(get_db)) -> DataSyncStatusResponse:
    recalls_count = (await db.execute(select(func.count()).select_from(RecallModel))).scalar_one()
    enforcements_count = (await db.execute(select(func.count()).select_from(EnforcementModel))).scalar_one()
    sync = get_public_sync_state()
    last_sync_at = sync.get("last_sync_at")
    return DataSyncStatusResponse(
        recalls_db_count=recalls_count,
        enforcements_db_count=enforcements_count,
        recall_cache_last_updated=last_sync_at,
        sanction_cache_last_updated=last_sync_at,
        last_sync_at=last_sync_at,
        sync_wave=sync.get("sync_wave"),
        sync_slot=sync.get("sync_slot"),
    )


@router.post("/trigger", response_model=DataSyncTriggerResponse)
async def data_sync_trigger(_req: DataSyncTriggerRequest) -> DataSyncTriggerResponse:
    result = await trigger_manual_staggered_sync()
    if result.get("started"):
        message = "백그라운드에서 동기화가 시작되었습니다. 잠시 후 새로고침해서 확인하세요."
    else:
        message = "이미 동기화가 진행 중입니다."
    return DataSyncTriggerResponse(started=result.get("started", False), message=message)
