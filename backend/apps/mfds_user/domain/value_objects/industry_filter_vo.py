from pydantic import BaseModel
from typing import List

# UI 카테고리에 없어도 일일 브리핑 조사·크롤링에 항상 포함
COMMON_REPORT_KEYWORDS: tuple[str, ...] = ("위생", "안전")


class IndustryFilter(BaseModel):
    media_codes: List[str]
    foodtype_mid_codes: List[str]
    crawler_params: List[str]
    keywords: List[str]

    def to_section_codes(self) -> List[str]:
        return self.crawler_params

    def to_keywords(self) -> List[str]:
        """선택 업종 키워드 + 공통 키워드(위생·안전)."""
        merged: list[str] = []
        seen: set[str] = set()
        for kw in [*self.keywords, *COMMON_REPORT_KEYWORDS]:
            term = (kw or "").strip()
            if term and term not in seen:
                seen.add(term)
                merged.append(term)
        return merged
