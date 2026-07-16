from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoutCommand:
    """어드민이 입력한 원본 명령 — 실행 모드·시드 URL·자연어 지시."""

    mode: str  # "crawler" | "scraper"
    url: str
    command: str


@dataclass(frozen=True)
class ScoutPlan:
    """자연어 명령을 해석해 얻은 실행 계획."""

    max_pages: int = 20
    max_depth: int = 2
    max_items: int = 50
    keywords: list[str] = field(default_factory=list)
    reason: str = ""


@dataclass(frozen=True)
class ScoutResult:
    """스카우트 1회 실행 결과 — 해석 계획 + 실행 요약."""

    mode: str
    plan: ScoutPlan
    summary: dict[str, object]
