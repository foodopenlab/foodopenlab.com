from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_isidor_couple_schema import IsidorCoupleSchema
from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorCoupleUseCase
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleResponse
from titanic.dependencies.passenger_isidor_couple_provider import get_isidor_couple_use_case

'''
이시도르 스트라우스 (Isidor Straus)
마시 백화점 공동 창업자. 아내와 함께 침실에서 기다리며 사망한 부부입니다.
'''
passenger_isidor_couple_router = APIRouter(prefix="/isidor", tags=["isidor"])


@passenger_isidor_couple_router.get("/myself", response_model=IsidorCoupleSchema)
async def introduce_myself(
    isidor: IsidorCoupleUseCase = Depends(get_isidor_couple_use_case),
) -> IsidorCoupleResponse:
    return await isidor.introduce_myself(
        IsidorCoupleSchema(
            id=8,
            name="이시도르 스트라우스 (Isidor Straus)",
        )
    )
