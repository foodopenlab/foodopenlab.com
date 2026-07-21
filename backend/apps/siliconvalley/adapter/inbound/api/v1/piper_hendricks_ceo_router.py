from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_hendricks_ceo_schema import HendricksCeoSchema
from siliconvalley.adapter.inbound.Assemblers.piper_hendricks_ceo_assembler import response_to_schema
from siliconvalley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from siliconvalley.dependencies.piper_hendricks_ceo_provider import get_hendricks_use_case

"""
헨드릭스 CEO (Hendricks CEO)
CEO
"""
hendricks_router = APIRouter(prefix="/hendricks", tags=["hendricks"])


@hendricks_router.get("/myself", response_model=HendricksCeoSchema)
async def introduce_myself(
    character: HendricksCeoUseCase = Depends(get_hendricks_use_case),
) -> HendricksCeoSchema:
    dto = await character.introduce_myself()
    return response_to_schema(dto)
