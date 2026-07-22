from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Destination(str, Enum):
    """시맨틱 분류 목적지."""

    SEARCH = "search"    # 단순 데이터 조회(자연어 검색)
    RAG = "rag"          # 사내 도메인 지식 기반 답변(EXAONE + 온톨로지)
    GENERAL = "general"  # 일상·상식·잡담 → Gemini
    REJECT = "reject"    # 보안·민감정보 요청 → 차단

    @classmethod
    def from_str(cls, value: object) -> "Destination":
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            # 분류 실패 시 일반 대화로 우회(RAG는 컨텍스트 없으면 막히므로 GENERAL이 안전)
            return cls.GENERAL


@dataclass(frozen=True)
class Intent:
    destination: Destination
    entities: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SemanticQuery:
    question: str
    client_ip: str | None = None


@dataclass(frozen=True)
class SemanticResult:
    answer: str
    destination: str
    blocked: bool = False
