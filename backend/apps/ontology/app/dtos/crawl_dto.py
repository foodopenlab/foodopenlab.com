from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CrawlRequest:
    """크롤 실행 파라미터. seed·keywords가 주어지면 Redis 소스 대신 그 값을 쓴다."""

    max_pages: int = 20
    max_depth: int = 2
    seed: str | None = None
    keywords: list[str] | None = None
    # 찾은 URL을 스크래퍼 큐(Redis)에 자동 적재할지. 스카우트 경로는 사용자가
    # resources 결과를 직접 필터링해 적재하므로 False로 끈다.
    enqueue_to_scraper: bool = True


@dataclass(frozen=True)
class CrawlFinding:
    """크롤러가 찾은 관련 페이지 1건 — resources 파일에 저장되는 단위."""

    url: str
    title: str = ""
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CrawlReport:
    """크롤 1회 실행 결과 요약."""

    seed: str | None
    keywords: list[str] = field(default_factory=list)
    pages_visited: int = 0
    urls_enqueued: int = 0
    findings_saved: int = 0
