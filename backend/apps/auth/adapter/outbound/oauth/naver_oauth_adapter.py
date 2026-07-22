from __future__ import annotations

from auth.adapter.outbound.oauth.base_oauth_adapter import BaseOAuthAdapter
from auth.app.dtos.auth_dto import OAuthProfile


class NaverOAuthAdapter(BaseOAuthAdapter):
    provider = "naver"
    env_prefix = "NAVER"
    authorize_endpoint = "https://nid.naver.com/oauth2.0/authorize"
    token_endpoint = "https://nid.naver.com/oauth2.0/token"
    userinfo_endpoint = "https://openapi.naver.com/v1/nid/me"
    scope = ""  # 네이버는 콘솔의 '제공 정보'로 결정, scope 파라미터 불필요

    def _augment_token_data(self, data: dict, state: str) -> dict:
        data["state"] = state  # 네이버 토큰 교환은 state 요구
        return data

    def _parse_profile(self, data: dict) -> OAuthProfile:
        resp = data.get("response") or {}
        return OAuthProfile(
            provider=self.provider,
            provider_id=str(resp.get("id", "")),
            email=(resp.get("email") or "").strip(),
            name=(resp.get("name") or resp.get("nickname") or "네이버 사용자").strip(),
            picture=resp.get("profile_image"),
        )
