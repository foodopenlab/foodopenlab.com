from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScrapeRequest:
    """스크랩 실행 파라미터 — 처리할 최대 URL 개수."""

    max_items: int = 50


@dataclass(frozen=True)
class ScrapedItem:
    """스크랩된 한 페이지의 정제 전(raw) 결과. 파일로 저장 후 사용자가 정제한다."""

    url: str
    title: str
    matched_keywords: list[str] = field(default_factory=list)
    snippet: str = ""
    content: str = ""
    content_length: int = 0


@dataclass(frozen=True)
class ScrapeReport:
    """스크랩 1회 실행 결과 요약."""

    urls_processed: int = 0
    items_scraped: int = 0
