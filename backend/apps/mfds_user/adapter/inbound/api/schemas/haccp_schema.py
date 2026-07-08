from typing import List, Optional

from pydantic import BaseModel, Field


class HaccpProductInfoResponse(BaseModel):
    found: bool = Field(..., description="품목 조회 성공 여부")
    prdlst_report_no: str = Field("", description="품목보고번호")
    product_name: Optional[str] = Field(default=None, description="제품명")
    manufacturer: Optional[str] = Field(default=None, description="제조사")
    raw_materials: List[str] = Field(default_factory=list, description="원재료 목록")
    allergens: List[str] = Field(default_factory=list, description="알레르기 유발 성분")
    nutrient_info: Optional[str] = Field(default=None, description="영양 정보")
    image_urls: List[str] = Field(default_factory=list, description="이미지 URL 목록")
    barcode: Optional[str] = Field(default=None, description="바코드")

    model_config = {
        "json_schema_extra": {
            "example": {
                "found": True,
                "prdlst_report_no": "20190101001",
                "product_name": "예시 제품",
                "manufacturer": "예시 제조사",
                "raw_materials": ["밀가루", "설탕"],
                "allergens": ["밀"],
                "nutrient_info": None,
                "image_urls": [],
                "barcode": "8801234567890",
            }
        }
    }
