from __future__ import annotations

from mfds_user.adapter.outbound.oauth.google_oauth_adapter import GoogleOAuthAdapter
from mfds_user.adapter.outbound.oauth.kakao_oauth_adapter import KakaoOAuthAdapter
from mfds_user.adapter.outbound.oauth.naver_oauth_adapter import NaverOAuthAdapter
from mfds_user.app.ports.output.oauth_provider_port import OAuthProviderPort

_PROVIDERS: dict[str, type[OAuthProviderPort]] = {
    "google": GoogleOAuthAdapter,
    "kakao": KakaoOAuthAdapter,
    "naver": NaverOAuthAdapter,
}


def get_oauth_provider(provider: str) -> OAuthProviderPort:
    """provider 문자열 → 어댑터 인스턴스 (Factory). 미지원 시 ValueError."""
    cls = _PROVIDERS.get(provider)
    if cls is None:
        raise ValueError(f"지원하지 않는 소셜 로그인 제공사입니다: {provider}")
    return cls()
