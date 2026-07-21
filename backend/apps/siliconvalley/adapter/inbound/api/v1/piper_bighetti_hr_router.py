from fastapi import APIRouter, Depends

from siliconvalley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema
from siliconvalley.adapter.inbound.Assemblers.piper_bighetti_hr_assembler import response_to_schema
from siliconvalley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from siliconvalley.dependencies.piper_bighetti_hr_provider import get_bighetti_use_case

"""
빅헤티 HR (Bighetti HR)
HR 담당
"""
bighetti_router = APIRouter(prefix="/bighetti", tags=["bighetti"])


@bighetti_router.get("/myself", response_model=BighettiHrSchema)
async def introduce_myself(
    character: BighettiHrUseCase = Depends(get_bighetti_use_case),
) -> BighettiHrSchema:
    dto = await character.introduce_myself()
    return response_to_schema(dto)
