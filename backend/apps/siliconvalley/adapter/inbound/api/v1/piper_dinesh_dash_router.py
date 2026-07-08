from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_dinesh_dash_schema import DineshDashSchema
from siliconvalley.adapter.inbound.Assemblers.piper_dinesh_dash_assembler import (
    response_to_schema,
    schema_to_query,
)
from siliconvalley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from siliconvalley.dependencies.piper_dinesh_dash_provider import get_dinesh_use_case

"""
디네시 대시 (Dinesh Dash)
대시보드 담당
"""
dinesh_router = APIRouter(prefix="/dinesh", tags=["dinesh"])


@dinesh_router.get("/myself", response_model=DineshDashSchema)
async def introduce_myself(
    character: DineshDashUseCase = Depends(get_dinesh_use_case),
) -> DineshDashSchema:
    query = schema_to_query(
        DineshDashSchema(
            id=2,
            name="디네시 대시 (Dinesh Dash)",
        )
    )
    dto = await character.introduce_myself(query)
    return response_to_schema(dto)
