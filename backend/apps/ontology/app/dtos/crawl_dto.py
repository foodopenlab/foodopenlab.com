from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawlRequest:
    """크롤 실행 파라미터. seed·keywords가 주어지면 Redis 소스 대신 그 값을 쓴다."""

    max_pages: int = 20
    max_depth: int = 2
    seed: str | None = None
    keywords: list[str] | None = None


@dataclass(frozen=True)
class CrawlReport:
    """크롤 1회 실행 결과 요약."""

    seed: str | None
    keywords: list[str] = field(default_factory=list)
    pages_visited: int = 0
    urls_enqueued: int = 0
