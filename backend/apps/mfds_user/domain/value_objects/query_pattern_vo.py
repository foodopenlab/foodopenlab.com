from enum import Enum

class QueryPattern(str, Enum):
    LAW        = "law"
    INGREDIENT = "ingredient"
    HACCP      = "haccp"
    GENERAL    = "general"

PATTERN_KEYWORDS = {
    QueryPattern.LAW:        ["고시", "기준", "규정", "식품위생법", "조항", "법률", "시행령", "시행규칙"],
    QueryPattern.INGREDIENT: ["원료", "첨가물", "배합", "성분", "사용기준", "원재료", "함량", "규격"],
    QueryPattern.HACCP:      ["CCP", "한계기준", "위해요소", "관리계획", "모니터링", "검증", "개선조치", "HACCP"],
}

def classify_pattern(question: str) -> QueryPattern:
    for pattern, keywords in PATTERN_KEYWORDS.items():
        if any(k in question for k in keywords):
            return pattern
    return QueryPattern.GENERAL
