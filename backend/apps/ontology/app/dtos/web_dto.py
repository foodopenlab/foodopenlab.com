from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FetchedPage:
    """웹 페치 결과 — 크롤러·스크래퍼가 공유하는 파싱된 페이지 스냅샷.

    파싱(링크/텍스트 추출)은 어댑터가 담당하고, 유스케이스는 이 순수 DTO만 다룬다.
    status_code == 0 은 네트워크 오류 등으로 페치에 실패한 경우를 뜻한다.
    """

    url: str
    status_code: int
    title: str = ""
    text: str = ""
    links: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.status_code == 200
