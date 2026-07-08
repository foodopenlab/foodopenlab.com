import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse
from titanic.dependencies.crew_hartley_violin_provider import get_hartley_violin_use_case

'''
월리스 하틀리 (Wallace Hartley)
침몰 당시 바이올린을 연주하며 승객들을 달랜 승무원 밴드 리더입니다.
'''
hartley_violin_router = APIRouter(prefix="/hartley", tags=["hartley"])


@hartley_violin_router.get("/myself", response_model=HartleyViolinSchema)
async def introduce_myself(
    hartley: HartleyViolinUseCase = Depends(get_hartley_violin_use_case),
) -> HartleyViolinResponse:
    return await hartley.introduce_myself(
        HartleyViolinSchema(
            id=3,
            name="월리스 하틀리 (Wallace Hartley)",
        )
    )


@hartley_violin_router.get("/correlation")
async def get_correlation_heatmap(
    hartley: HartleyViolinUseCase = Depends(get_hartley_violin_use_case),
) -> StreamingResponse:
    png_bytes = await hartley.get_correlation_heatmap()
    return StreamingResponse(io.BytesIO(png_bytes), media_type="image/png")
