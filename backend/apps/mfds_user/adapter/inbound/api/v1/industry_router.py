from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from mfds_user.app.ports.input.industry_use_case import IndustryUseCase
from mfds_user.dependencies.industry import get_industry_use_case
from mfds_user.adapter.inbound.api.schemas.industry_schema import (
    MyIndustryResponseSchema,
    UpdateMyIndustryRequestSchema,
    IndustryCategorySchema,
    UpdateKeywordsRequestSchema,
    FoodtypeSelectionItem
)

router = APIRouter(prefix="", tags=["industry"])

@router.get("/mypage/industry", response_model=MyIndustryResponseSchema)
async def get_my_industry(
    token: UserTokenPayload = Depends(verify_token),
    use_case: IndustryUseCase = Depends(get_industry_use_case)
) -> MyIndustryResponseSchema:
    user_id = UUID(token.sub)
    selections = await use_case.get_my_industry(user_id)
    
    all_categories = await use_case.get_all_categories()
    cat_map = {c.code: c for c in all_categories}
    
    media_codes = []
    foodtype_selections = []
    
    for sel in selections:
        cat = cat_map.get(sel.category_code)
        if cat:
            if cat.type == "media":
                media_codes.append(sel.category_code)
            elif cat.type == "foodtype":
                foodtype_selections.append(
                    FoodtypeSelectionItem(
                        code=sel.category_code,
                        parent_code=cat.parent_code
                    )
                )
                
    return MyIndustryResponseSchema(
        media_codes=media_codes,
        foodtype_selections=foodtype_selections
    )

@router.put("/mypage/industry", status_code=status.HTTP_200_OK)
async def update_my_industry(
    req: UpdateMyIndustryRequestSchema,
    token: UserTokenPayload = Depends(verify_token),
    use_case: IndustryUseCase = Depends(get_industry_use_case)
):
    user_id = UUID(token.sub)
    try:
        selections_dict = [
            {"code": item.code, "parent_code": item.parent_code}
            for item in req.foodtype_selections
        ]
        await use_case.update_my_industry(user_id, req.media_codes, selections_dict)
        return {"message": "업종 설정이 성공적으로 업데이트되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/admin/industry-categories", response_model=List[IndustryCategorySchema])
async def get_all_categories(
    use_case: IndustryUseCase = Depends(get_industry_use_case)
) -> List[IndustryCategorySchema]:
    categories = await use_case.get_all_categories()
    return [
        IndustryCategorySchema(
            code=c.code,
            type=c.type.value,
            parent_code=c.parent_code,
            depth=c.depth,
            is_flat=c.is_flat,
            name_ko=c.name_ko,
            crawler_param=c.crawler_param,
            keywords=c.keywords
        )
        for c in categories
    ]

@router.put("/admin/industry-categories/{code}", status_code=status.HTTP_200_OK)
async def update_category_keywords(
    code: str,
    req: UpdateKeywordsRequestSchema,
    use_case: IndustryUseCase = Depends(get_industry_use_case)
):
    try:
        await use_case.update_category_keywords(code, req.keywords)
        return {"message": f"카테고리 '{code}'의 키워드가 업데이트되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
