from __future__ import annotations

import logging
import os
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from mfds_user.app.ports.input.oauth_use_case import OAuthUseCase
from mfds_user.dependencies.oauth import get_oauth_use_case

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["oauth"])


def _frontend_url() -> str:
    return (os.getenv("FRONTEND_URL") or "http://localhost:3000").rstrip("/")


@router.get("/{provider}/login")
async def oauth_login(
    provider: str,
    use_case: OAuthUseCase = Depends(get_oauth_use_case),
) -> RedirectResponse:
    """소셜 로그인 시작 — 제공사 동의 화면으로 리다이렉트."""
    try:
        authorize_url = await use_case.build_authorize_url(provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse(authorize_url, status_code=302)


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    use_case: OAuthUseCase = Depends(get_oauth_use_case),
) -> RedirectResponse:
    """제공사 콜백 — JWT 발급·Redis 저장 후 프론트로 토큰을 fragment로 전달."""
    frontend = _frontend_url()
    if error or not code or not state:
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)

    try:
        session = await use_case.handle_callback(provider, code, state)
    except ValueError as exc:
        logger.warning("[oauth_callback] provider=%s 실패: %s", provider, exc)
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)
    except Exception:
        logger.exception("[oauth_callback] provider=%s 예외", provider)
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)

    # 토큰은 쿼리가 아닌 fragment(#)로 전달 — 서버·Referer로 유출되지 않음.
    fragment = urlencode(
        {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
    )
    return RedirectResponse(f"{frontend}/auth/callback#{fragment}", status_code=302)
