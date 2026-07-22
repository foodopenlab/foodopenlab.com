from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AuthIdentity:
    """auth가 소유하는 최소 신원(1행 = 소셜 계정 1개).

    토큰의 sub는 이 엔티티의 id, roles는 발급 시 클레임에 실린다.
    """

    provider: str
    provider_id: str
    email: str
    name: str
    roles: list[str] = field(default_factory=lambda: ["user"])
    id: str | None = None  # 공유 유저 테이블의 UUID(문자열)
    created_at: datetime | None = None
