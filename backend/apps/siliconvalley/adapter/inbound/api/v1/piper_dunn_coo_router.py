from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from siliconvalley.adapter.inbound.Assemblers.piper_dunn_coo_assembler import (
    response_to_schema,
    schema_to_query,
)
from siliconvalley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from siliconvalley.dependencies.piper_dunn_coo_provider import get_dunn_use_case

"""
던 COO (Dunn COO)
COO
"""
dunn_router = APIRouter(prefix="/dunn", tags=["dunn"])


@dunn_router.get("/myself", response_model=DunnCooSchema)
async def introduce_myself(
    character: DunnCooUseCase = Depends(get_dunn_use_case),
) -> DunnCooSchema:
    query = schema_to_query(
        DunnCooSchema(
            id=3,
            name="던 COO (Dunn COO)",
        )
    )
    dto = await character.introduce_myself(query)
    return response_to_schema(dto)
