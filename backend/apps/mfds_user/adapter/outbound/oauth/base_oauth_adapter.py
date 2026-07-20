from __future__ import annotations

import logging
import os
from urllib.parse import urlencode

import httpx

from mfds_user.app.dtos.oauth_dto import OAuthProfile
from mfds_user.app.ports.output.oauth_provider_port import OAuthProviderPort

logger = logging.getLogger(__name__)


class BaseOAuthAdapter(OAuthProviderPort):
    """OAuth2 Authorization Code 공통 흐름 — Template Method.

    provider별로 엔드포인트·scope·프로필 파싱만 다르다.
    """

    provider: str = ""
    env_prefix: str = ""
    authorize_endpoint: str = ""
    token_endpoint: str = ""
    userinfo_endpoint: str = ""
    scope: str = ""

    def _conf(self) -> tuple[str, str, str]:
        client_id = (os.getenv(f"{self.env_prefix}_CLIENT_ID") or "").strip()
        client_secret = (os.getenv(f"{self.env_prefix}_CLIENT_SECRET") or "").strip()
        redirect_uri = (os.getenv(f"{self.env_prefix}_REDIRECT_URI") or "").strip()
        if not client_id or not redirect_uri:
            raise ValueError(
                f"{self.provider} OAuth 설정이 없습니다 "
                f"(.env {self.env_prefix}_CLIENT_ID / {self.env_prefix}_REDIRECT_URI 확인)."
            )
        return client_id, client_secret, redirect_uri

    def authorize_url(self, state: str) -> str:
        client_id, _, redirect_uri = self._conf()
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        if self.scope:
            params["scope"] = self.scope
        return f"{self.authorize_endpoint}?{urlencode(params)}"

    def _augment_token_data(self, data: dict, state: str) -> dict:
        """provider가 토큰 요청에 추가 파라미터가 필요하면 override."""
        return data

    async def fetch_profile(self, code: str, state: str) -> OAuthProfile:
        client_id, client_secret, redirect_uri = self._conf()
        token_data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if client_secret:
            token_data["client_secret"] = client_secret
        token_data = self._augment_token_data(token_data, state)

        async with httpx.AsyncClient(timeout=15) as client:
            token_resp = await client.post(
                self.token_endpoint,
                data=token_data,
                headers={"Accept": "application/json"},
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get("access_token")
            if not access_token:
                raise ValueError(f"{self.provider} 액세스 토큰 교환에 실패했습니다.")

            info_resp = await client.get(
                self.userinfo_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            info_resp.raise_for_status()
            return self._parse_profile(info_resp.json())

    def _parse_profile(self, data: dict) -> OAuthProfile:  # pragma: no cover - abstract-ish
        raise NotImplementedError
