from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawlRequest:
    """크롤 실행 파라미터 — 시드·키워드는 Redis에서 가져오므로 여기엔 한도만 담는다."""

    max_pages: int = 20
    max_depth: int = 2


@dataclass(frozen=True)
class CrawlReport:
    """크롤 1회 실행 결과 요약."""

    seed: str | None
    keywords: list[str] = field(default_factory=list)
    pages_visited: int = 0
    urls_enqueued: int = 0
