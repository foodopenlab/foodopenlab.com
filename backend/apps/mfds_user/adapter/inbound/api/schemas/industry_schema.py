from typing import List, Optional

from pydantic import BaseModel, Field


class IndustryCategorySchema(BaseModel):
    code: str = Field(..., description="업종 코드")
    type: str = Field(..., description="카테고리 유형")
    parent_code: Optional[str] = Field(default=None, description="상위 코드")
    depth: int = Field(..., description="트리 깊이")
    is_flat: bool = Field(..., description="평면 노드 여부")
    name_ko: str = Field(..., description="한글 명칭")
    crawler_param: Optional[str] = Field(default=None, description="크롤러 파라미터")
    keywords: List[str] = Field(default_factory=list, description="연관 키워드")


class FoodtypeSelectionItem(BaseModel):
    code: str = Field(..., description="식품유형 코드")
    parent_code: Optional[str] = Field(default=None, description="상위 식품유형 코드")


class MyIndustryResponseSchema(BaseModel):
    media_codes: List[str] = Field(default_factory=list, description="선택 미디어 코드")
    foodtype_selections: List[FoodtypeSelectionItem] = Field(
        default_factory=list,
        description="선택 식품유형",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "media_codes": ["M001"],
                "foodtype_selections": [{"code": "FT01", "parent_code": None}],
            }
        }
    }


class UpdateMyIndustryRequestSchema(BaseModel):
    media_codes: List[str] = Field(default_factory=list, description="선택 미디어 코드")
    foodtype_selections: List[FoodtypeSelectionItem] = Field(
        default_factory=list,
        description="선택 식품유형",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "media_codes": ["M001", "M002"],
                "foodtype_selections": [{"code": "FT01", "parent_code": None}],
            }
        }
    }


class UpdateKeywordsRequestSchema(BaseModel):
    keywords: List[str] = Field(default_factory=list, description="업종 키워드 목록")

    model_config = {
        "json_schema_extra": {
            "example": {
                "keywords": ["유제품", "발효유"],
            }
        }
    }
