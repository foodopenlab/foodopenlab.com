from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_gilfoyle_sys_schema import GilfoyleSysSchema
from siliconvalley.adapter.inbound.Assemblers.piper_gilfoyle_sys_assembler import (
    response_to_schema,
    schema_to_query,
)
from siliconvalley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from siliconvalley.dependencies.piper_gilfoyle_sys_provider import get_gilfoyle_use_case

"""
Gilfoyle Sys
시스템 담당
"""
gilfoyle_router = APIRouter(prefix="/gilfoyle", tags=["gilfoyle"])


@gilfoyle_router.get("/myself", response_model=GilfoyleSysSchema)
async def introduce_myself(
    character: GilfoyleSysUseCase = Depends(get_gilfoyle_use_case),
) -> GilfoyleSysSchema:
    query = schema_to_query(
        GilfoyleSysSchema(
            id=4,
            name="Gilfoyle Sys",
        )
    )
    dto = await character.introduce_myself(query)
    return response_to_schema(dto)
