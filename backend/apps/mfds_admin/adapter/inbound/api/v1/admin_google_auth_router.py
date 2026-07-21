from __future__ import annotations

import logging
import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from matrix.grid_google_oauth_manager import build_authorize_url, fetch_google_identity
from mfds_admin.app.exceptions import AdminAuthError, AdminConfigError
from mfds_admin.app.ports.input.admin_google_auth_use_case import AdminGoogleAuthUseCase
from mfds_admin.dependencies.admin_google_auth import get_admin_google_auth_use_case

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin-auth"])

_STATE_COOKIE = "admin_oauth_state"
_NEXT_COOKIE = "admin_oauth_next"
DOCS_SESSION_COOKIE = "admin_docs_session"


def _redirect_uri() -> str:
    return (os.getenv("ADMIN_GOOGLE_REDIRECT_URI") or "").strip()


def _admin_frontend_base() -> str:
    return (os.getenv("ADMIN_FRONTEND_URL") or os.getenv("FRONTEND_URL") or "http://localhost:3000").rstrip("/")


def _is_docs_target(next_target: str) -> bool:
    return next_target.startswith("/docs") or next_target.startswith("/redoc")


@router.get("/admin/auth/google/login")
async def admin_google_login(next: str = "") -> RedirectResponse:
    """어드민 구글 로그인 시작 — state를 쿠키에 심고 구글 동의화면으로 리다이렉트."""
    redirect_uri = _redirect_uri()
    if not redirect_uri:
        return RedirectResponse(f"{_admin_frontend_base()}/admin/login?error=config", status_code=302)

    state = secrets.token_urlsafe(24)
    resp = RedirectResponse(build_authorize_url(redirect_uri, state), status_code=302)
    secure = redirect_uri.startswith("https://")
    resp.set_cookie(_STATE_COOKIE, state, max_age=600, httponly=True, secure=secure, samesite="lax")
    resp.set_cookie(_NEXT_COOKIE, next or "", max_age=600, httponly=True, secure=secure, samesite="lax")
    return resp


@router.get("/admin/auth/google/callback")
async def admin_google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    use_case: AdminGoogleAuthUseCase = Depends(get_admin_google_auth_use_case),
) -> RedirectResponse:
    """구글 콜백 — state 검증·이메일 확인·admin JWT 발급. /docs면 세션 쿠키, 아니면 프론트로 토큰 전달."""
    front = _admin_frontend_base()
    redirect_uri = _redirect_uri()
    secure = redirect_uri.startswith("https://")
    cookie_state = request.cookies.get(_STATE_COOKIE)
    next_target = request.cookies.get(_NEXT_COOKIE) or ""

    def _fail(reason: str) -> RedirectResponse:
        r = RedirectResponse(f"{front}/admin/login?error={reason}", status_code=302)
        r.delete_cookie(_STATE_COOKIE)
        r.delete_cookie(_NEXT_COOKIE)
        return r

    if error or not code or not state:
        return _fail("oauth")
    if not cookie_state or not secrets.compare_digest(cookie_state, state):
        return _fail("state")

    try:
        email, name = await fetch_google_identity(code, redirect_uri)
        token_dto = await use_case.login_with_google(email, name)
    except AdminAuthError:
        return _fail("forbidden")
    except AdminConfigError:
        return _fail("config")
    except Exception:
        logger.exception("[admin_google_callback] 실패")
        return _fail("oauth")

    if _is_docs_target(next_target):
        resp = RedirectResponse(next_target, status_code=302)
        resp.set_cookie(
            DOCS_SESSION_COOKIE,
            token_dto.access_token,
            max_age=token_dto.expires_in,
            httponly=True,
            secure=secure,
            samesite="lax",
        )
    else:
        fragment = urlencode({"access_token": token_dto.access_token})
        resp = RedirectResponse(f"{front}/admin/auth/callback#{fragment}", status_code=302)

    resp.delete_cookie(_STATE_COOKIE)
    resp.delete_cookie(_NEXT_COOKIE)
    return resp
