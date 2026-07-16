from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeywordSet:
    """키워드 매칭 규칙(대소문자 무시 부분일치) — 순수 도메인 VO.

    크롤러(관련 페이지 판별)와 스크래퍼(매칭 키워드 추출)가 공유한다.
    프레임워크·I/O 의존 없이 텍스트 판정만 담당한다.
    """

    values: tuple[str, ...]

    @classmethod
    def of(cls, keywords: list[str]) -> KeywordSet:
        # 공백 제거·소문자화·중복 제거(원 표기는 매칭 결과 반환용으로 보존).
        seen: dict[str, str] = {}
        for kw in keywords:
            normalized = kw.strip()
            if normalized:
                seen.setdefault(normalized.lower(), normalized)
        return cls(tuple(seen.values()))

    @property
    def is_empty(self) -> bool:
        return not self.values

    def matches(self, text: str) -> list[str]:
        """text에 등장하는 키워드 목록(원 표기)을 반환한다."""
        haystack = text.lower()
        return [kw for kw in self.values if kw.lower() in haystack]

    def any_match(self, text: str) -> bool:
        """키워드가 비어 있으면 항상 True(필터 미적용)로 간주한다."""
        if self.is_empty:
            return True
        haystack = text.lower()
        return any(kw.lower() in haystack for kw in self.values)
