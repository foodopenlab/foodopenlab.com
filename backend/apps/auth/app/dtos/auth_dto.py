from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IssuedAccessToken:
    """발급된 access token + 세션 저장·블랙리스트에 필요한 메타(jti, 만료)."""

    token: str
    jti: str
    expires_at: datetime


@dataclass(frozen=True)
class RefreshRotation:
    """refresh 로테이션 결과 — 검증된 sub와 새로 발급된 refresh 토큰."""

    sub: str
    refresh_token: str


@dataclass(frozen=True)
class OAuthProfile:
    """소셜 제공사에서 정규화한 프로필."""

    provider: str          # 'google' | 'kakao' | 'naver'
    provider_id: str       # 제공사 고유 subject
    email: str             # 없으면 상위에서 합성 이메일로 채움
    name: str
    picture: str | None = None


@dataclass(frozen=True)
class TokenBundle:
    """로그인·리프레시 성공 시 클라이언트에 반환하는 토큰 묶음."""

    access_token: str
    refresh_token: str
    expires_in: int
    sub: str
    roles: list[str]
    token_type: str = "Bearer"
