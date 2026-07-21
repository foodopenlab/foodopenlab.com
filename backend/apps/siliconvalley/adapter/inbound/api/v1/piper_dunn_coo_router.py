from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from siliconvalley.adapter.inbound.Assemblers.piper_dunn_coo_assembler import response_to_schema
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
    dto = await character.introduce_myself()
    return response_to_schema(dto)
