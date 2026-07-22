from __future__ import annotations

from auth.adapter.outbound.oauth.base_oauth_adapter import BaseOAuthAdapter
from auth.app.dtos.auth_dto import OAuthProfile


class KakaoOAuthAdapter(BaseOAuthAdapter):
    provider = "kakao"
    env_prefix = "KAKAO"  # KAKAO_CLIENT_ID = REST API 키
    authorize_endpoint = "https://kauth.kakao.com/oauth/authorize"
    token_endpoint = "https://kauth.kakao.com/oauth/token"
    userinfo_endpoint = "https://kapi.kakao.com/v2/user/me"
    scope = "profile_nickname account_email"

    def _parse_profile(self, data: dict) -> OAuthProfile:
        account = data.get("kakao_account") or {}
        profile = account.get("profile") or {}
        return OAuthProfile(
            provider=self.provider,
            provider_id=str(data.get("id", "")),
            email=(account.get("email") or "").strip(),
            name=(profile.get("nickname") or "카카오 사용자").strip(),
            picture=profile.get("profile_image_url"),
        )
