from fastapi import APIRouter, Depends, HTTPException, status
from mfds_user.app.ports.input.regulation_use_case import RegulationUseCase
from mfds_user.dependencies.regulation import get_regulation_use_case
from mfds_user.adapter.inbound.api.schemas.regulation_schema import RegulationListResponseSchema, RegulationItemSchema
from mfds_user.app.dtos.regulation_dto import RegulationSearchQuery

router = APIRouter(prefix="/regulation", tags=["regulation"])

@router.get("", response_model=RegulationListResponseSchema)
async def search_regulation(
    query: str,
    user_id: str | None = None,
    session_key: str | None = None,
    use_case: RegulationUseCase = Depends(get_regulation_use_case)
) -> RegulationListResponseSchema:
    if not query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="검색어를 입력해 주세요.")
    
    q = RegulationSearchQuery(
        query=query,
        user_id=user_id,
        session_key=session_key
    )
    res = await use_case.search_regulations(q)
    return RegulationListResponseSchema(
        items=[
            RegulationItemSchema(
                law_id=item.law_id,
                title=item.title,
                law_type=item.law_type.value,
                change_type=item.change_type,
                promulgation_date=item.promulgation_date,
                promulgation_no=item.promulgation_no,
                enforcement_date=item.enforcement_date,
                source=item.source,
                url=item.url
            )
            for item in res.items
        ],
        total=res.total
    )
