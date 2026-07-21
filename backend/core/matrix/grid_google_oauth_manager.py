"""전역 Google OAuth2(Authorization Code) 헬퍼 — 앱 간 공유 커널.

BC가 각자 Google 어댑터를 두면 중복·결합이 생기므로, 재사용 가능한 authorize URL 생성과
code→identity 교환을 여기에 둔다. redirect_uri는 호출자가 넘긴다(유저/어드민 흐름이 서로 다른 콜백을 사용).
"""
from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx

_AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"
_SCOPE = "openid email profile"


def _credentials() -> tuple[str, str]:
    client_id = (os.getenv("GOOGLE_CLIENT_ID") or "").strip()
    client_secret = (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip()
    if not client_id or not client_secret:
        raise ValueError("Google OAuth 설정이 없습니다 (.env GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET).")
    return client_id, client_secret


def build_authorize_url(redirect_uri: str, state: str) -> str:
    client_id, _ = _credentials()
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": _SCOPE,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{_AUTHORIZE_ENDPOINT}?{urlencode(params)}"


async def fetch_google_identity(code: str, redirect_uri: str) -> tuple[str, str]:
    """authorization code를 교환해 (email, name)을 반환한다."""
    client_id, client_secret = _credentials()
    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            _TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
            headers={"Accept": "application/json"},
        )
        token_resp.raise_for_status()
        access_token = token_resp.json().get("access_token")
        if not access_token:
            raise ValueError("Google 액세스 토큰 교환에 실패했습니다.")

        info_resp = await client.get(
            _USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        info_resp.raise_for_status()
        data = info_resp.json()

    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or data.get("email") or "").strip()
    if not email:
        raise ValueError("Google 프로필에서 이메일을 가져오지 못했습니다.")
    return email, name
