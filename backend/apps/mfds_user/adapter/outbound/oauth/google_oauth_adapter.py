from __future__ import annotations

from mfds_user.adapter.outbound.oauth.base_oauth_adapter import BaseOAuthAdapter
from mfds_user.app.dtos.oauth_dto import OAuthProfile


class GoogleOAuthAdapter(BaseOAuthAdapter):
    provider = "google"
    env_prefix = "GOOGLE"
    authorize_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
    scope = "openid email profile"

    def _parse_profile(self, data: dict) -> OAuthProfile:
        return OAuthProfile(
            provider=self.provider,
            provider_id=str(data.get("sub", "")),
            email=(data.get("email") or "").strip(),
            name=(data.get("name") or data.get("email") or "구글 사용자").strip(),
            picture=data.get("picture"),
        )
