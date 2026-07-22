from __future__ import annotations

from auth.adapter.outbound.oauth.base_oauth_adapter import BaseOAuthAdapter
from auth.app.dtos.auth_dto import OAuthProfile


class GoogleOAuthAdapter(BaseOAuthAdapter):
    provider = "google"
    env_prefix = "GOOGLE"
    authorize_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
    scope = "openid email profile"

    def _parse_profile(self, data: dict) -> OAuthProfile:
        return OAuthProfile(
            provider=self.provider,
            provider_id=str(data.get("sub", "")),
            email=(data.get("email") or "").strip(),
            name=(data.get("name") or "구글 사용자").strip(),
            picture=data.get("picture"),
        )
