from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse
from titanic.dependencies.passenger_cal_tester_provider import get_cal_tester_use_case

'''
칼 헉클리 (Caledon Hockley)
로즈의 약혼자이자 1등급 승객입니다.
'''
passenger_cal_tester_router = APIRouter(prefix="/cal", tags=["cal"])


@passenger_cal_tester_router.get("/myself", response_model=CalTesterSchema)
async def introduce_myself(
    cal: CalTesterUseCase = Depends(get_cal_tester_use_case),
) -> CalTesterResponse:
    return await cal.introduce_myself(
        CalTesterSchema(
            id=7,
            name="칼 헉클리 (Caledon Hockley)",
        )
    )
