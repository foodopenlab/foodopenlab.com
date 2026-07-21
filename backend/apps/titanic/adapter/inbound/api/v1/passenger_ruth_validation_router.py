from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_ruth_validation_schema import RuthValidationSchema
from titanic.app.ports.input.passenger_ruth_validation_use_case import RuthValidationUseCase
from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationQuery, RuthValidationResponse
from titanic.dependencies.passenger_ruth_validation_provider import get_ruth_validation_use_case

'''
루쓰 드윗 부카터 (Ruth DeWitt Bukater)
로즈의 어머니이자 1등급 승객입니다.
'''
passenger_ruth_validation_router = APIRouter(prefix="/ruth", tags=["ruth"])


@passenger_ruth_validation_router.get("/myself", response_model=RuthValidationSchema)
async def introduce_myself(
    ruth: RuthValidationUseCase = Depends(get_ruth_validation_use_case),
) -> RuthValidationResponse:
    return await ruth.introduce_myself(
        RuthValidationQuery(
            id=12,
            name="루쓰 드윗 부카터 (Ruth DeWitt Bukater)",
        )
    )
