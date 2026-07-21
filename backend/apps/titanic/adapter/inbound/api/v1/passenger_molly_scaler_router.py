from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema
from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.dependencies.passenger_molly_scaler_provider import get_molly_scaler_use_case

'''
몰리 브라운 (Margaret 'Molly' Brown)
구명정에 돌아가 추가 승객을 구하려 했던 1등급 승객입니다.
'''
passenger_molly_scaler_router = APIRouter(prefix="/molly", tags=["molly"])


@passenger_molly_scaler_router.get("/myself", response_model=MollyScalerSchema)
async def introduce_myself(
    molly: MollyScalerUseCase = Depends(get_molly_scaler_use_case),
) -> MollyScalerResponse:
    return await molly.introduce_myself(
        MollyScalerQuery(
            id=10,
            name="몰리 브라운 (Margaret 'Molly' Brown)",
        )
    )
