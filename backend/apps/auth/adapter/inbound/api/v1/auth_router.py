from __future__ import annotations

import logging
import os
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from auth.adapter.inbound.api.schemas.auth_schema import (
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from auth.adapter.inbound.mappers.auth_mapper import to_token_response
from auth.adapter.outbound.token.jwks_provider import build_jwks
from auth.app.ports.input.auth_use_case import IAuthUseCase
from auth.dependencies.auth_provider import get_auth_use_case
from auth.domain.exceptions import InvalidRefreshError, RefreshReuseError
from auth.domain.value_objects.role import Role
from matrix.grid_seraph_token_guard_manager import RoleChecker, TokenPayload, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
wellknown_router = APIRouter(tags=["auth"])  # /.well-known 은 prefix 밖


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "auth"}


@router.get("/protected-demo")
async def protected_demo(
    user: TokenPayload = Depends(RoleChecker(Role.ADMIN.value)),
) -> dict:
    """RBAC 가드 시연 — admin 역할 토큰만 통과(그 외 403, 무토큰 401).

    Phase 5: 기존 앱을 건드리지 않고 auth 자체에 보호 패턴을 시연한다.
    실제 앱 보호는 프론트가 auth RS256 토큰을 사용하게 된 뒤(I3) 적용한다.
    """
    return {"sub": user.sub, "roles": user.roles, "message": "admin 전용 리소스 접근 성공"}


@router.get("/{provider}/login")
async def oauth_login(
    provider: str,
    use_case: IAuthUseCase = Depends(get_auth_use_case),
) -> RedirectResponse:
    """소셜 로그인 시작 — 제공사 동의 화면으로 리다이렉트."""
    try:
        url = await use_case.build_authorize_url(provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return RedirectResponse(url, status_code=302)


def _frontend_url() -> str:
    return (os.getenv("FRONTEND_URL") or "http://localhost:3000").rstrip("/")


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    use_case: IAuthUseCase = Depends(get_auth_use_case),
) -> RedirectResponse:
    """제공사 콜백 → 신원 upsert → 토큰 발급 → 프론트로 리다이렉트.

    토큰은 쿼리가 아닌 fragment(#)로 전달 — 서버 로그·Referer로 유출되지 않는다.
    """
    frontend = _frontend_url()
    if error or not code or not state:
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)
    try:
        bundle = await use_case.handle_callback(provider, code, state)
    except ValueError as exc:
        logger.warning("[oauth_callback] provider=%s 실패: %s", provider, exc)
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)
    except Exception:
        logger.exception("[oauth_callback] provider=%s 예외", provider)
        return RedirectResponse(f"{frontend}/login?oauth_error=1", status_code=302)

    fragment = urlencode(
        {"access_token": bundle.access_token, "refresh_token": bundle.refresh_token}
    )
    return RedirectResponse(f"{frontend}/auth/callback#{fragment}", status_code=302)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    body: RefreshRequest,
    response: Response,
    use_case: IAuthUseCase = Depends(get_auth_use_case),
) -> TokenResponse:
    try:
        bundle = await use_case.refresh(body.refresh_token)
    except RefreshReuseError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except InvalidRefreshError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    _set_access_cookie(response, bundle.access_token, bundle.expires_in)
    return to_token_response(bundle)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    response: Response,
    current: TokenPayload = Depends(get_current_user),
    use_case: IAuthUseCase = Depends(get_auth_use_case),
) -> dict:
    await use_case.logout(current, body.refresh_token)
    response.delete_cookie("access_token")
    return {"ok": True}


@wellknown_router.get("/.well-known/jwks.json")
async def jwks() -> dict:
    """공개키를 JWK(kid 포함)로 노출 — 외부/백엔드 검증자용."""
    return build_jwks()


def _set_access_cookie(response: Response, token: str, max_age: int) -> None:
    # 로컬/모놀리스 단계는 domain 미지정. Phase 6에서 domain=".foodopenlab.com".
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="lax",
    )
