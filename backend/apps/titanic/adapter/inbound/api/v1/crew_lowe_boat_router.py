from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatResponse
from titanic.dependencies.crew_lowe_boat_provider import get_lowe_boat_use_case

'''
해롤드 로우 (Harold Lowe)
구명정을 운용하며 여러 명을 구한 다섯 번째 항해사입니다.
'''
lowe_boat_router = APIRouter(prefix="/lowe", tags=["lowe"])


@lowe_boat_router.get("/myself", response_model=LoweBoatSchema)
async def introduce_myself(
    lowe: LoweBoatUseCase = Depends(get_lowe_boat_use_case),
) -> LoweBoatResponse:
    return await lowe.introduce_myself(
        LoweBoatSchema(
            id=4,
            name="해롤드 로우 (Harold Lowe)",
        )
    )
