from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer_use_case

'''
잭 도슨 (Jack Dawson)
3등급 승객이자 영화 속 주인공입니다.
'''
passenger_jack_trainer_router = APIRouter(prefix="/jack", tags=["jack"])


@passenger_jack_trainer_router.get("/myself", response_model=JackTrainerSchema)
async def introduce_myself(
    jack: JackTrainerUseCase = Depends(get_jack_trainer_use_case),
) -> JackTrainerResponse:
    return await jack.introduce_myself(
        JackTrainerSchema(
            id=9,
            name="잭 도슨 (Jack Dawson)",
        )
    )
