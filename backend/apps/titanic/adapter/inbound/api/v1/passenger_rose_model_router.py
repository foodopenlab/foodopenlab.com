from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case

'''
로즈 드윗 부카터 (Rose DeWitt Bukater)
1등급 승객이자 영화 속 주인공입니다.
'''
passenger_rose_model_router = APIRouter(prefix="/rose", tags=["rose"])


@passenger_rose_model_router.get("/myself", response_model=RoseModelSchema)
async def introduce_myself(
    rose: RoseModelUseCase = Depends(get_rose_model_use_case),
) -> RoseModelResponse:
    return await rose.introduce_myself(
        RoseModelQuery(
            id=11,
            name="로즈 드윗 부카터 (Rose DeWitt Bukater)",
        )
    )
