"""OAuth2 Authorization Code 공통 흐름 — Template Method.

provider별로 엔드포인트·scope·프로필 파싱만 다르다. env에서 client id/secret/redirect를 읽는다.
(mfds_user의 동일 패턴을 apps/auth 자기완결로 복제 — BC 간 정당한 중복, spoke→spoke import 금지.)
"""

from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx

from auth.app.dtos.auth_dto import OAuthProfile
from auth.app.ports.output.oauth_provider_port import IOAuthProviderPort


class BaseOAuthAdapter(IOAuthProviderPort):
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

    def _parse_profile(self, data: dict) -> OAuthProfile:
        raise NotImplementedError
