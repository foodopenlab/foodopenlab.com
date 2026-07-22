"""Seraph — 매트릭스의 문지기. RS256 토큰 검증 공유커널.

발급(개인키)은 `apps/auth` 안에만 존재하고, **검증은 공개키만으로 이곳에서** 수행한다.
모든 백엔드 컨테이너가 이 매니저를 통해 토큰을 검증한다(발급 코드 import 금지).

- 허용 알고리즘은 `algorithms=["RS256"]` 리터럴 하드코딩 (auth BC 규칙 3).
- 개인키(JWT_PRIVATE_KEY)는 이 파일 어디에서도 참조하지 않는다 (규칙 4).
- 기존 `grid_admin_guard_manager`(HS256 어드민)와 병렬 공존한다.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
from dataclasses import dataclass, field
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidTokenError,
)

logger = logging.getLogger(__name__)

_ALGORITHMS = ["RS256"]  # 리터럴 하드코딩 — 환경변수로 빼지 않는다(규칙 3).
_DEFAULT_AUD = "foodopenlab-api"


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    aud: str
    exp: int
    roles: list[str] = field(default_factory=list)
    email: str | None = None
    name: str | None = None
    iat: int | None = None
    jti: str | None = None


def _public_key() -> str:
    """검증 공개키(PEM)를 호출 시점에 로드. base64 우선, 원문 PEM 폴백."""
    b64 = (os.getenv("JWT_PUBLIC_KEY_B64") or "").strip()
    if b64:
        return base64.b64decode(b64).decode("utf-8")
    raw = (os.getenv("JWT_PUBLIC_KEY") or "").strip()
    if raw:
        return raw
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="인증 검증 키(JWT_PUBLIC_KEY)가 설정되지 않았습니다.",
    )


def _service_aud() -> str:
    return (os.getenv("SERVICE_AUD") or _DEFAULT_AUD).strip()


def verify_token(token: str, aud: str) -> TokenPayload:
    """RS256 서명·만료·aud 검증 후 payload 반환. 실패 시 HTTPException.

    - 만료 → 401
    - aud 불일치 → 403
    - 서명 변조·`alg=none`·`alg=HS256` 강제·형식 오류 → 401
    """
    try:
        claims = jwt.decode(
            token,
            _public_key(),
            algorithms=_ALGORITHMS,
            audience=aud,
            options={"require": ["exp", "sub", "aud"]},
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰이 만료되었습니다") from exc
    except InvalidAudienceError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="토큰 대상(aud)이 일치하지 않습니다") from exc
    except InvalidTokenError as exc:
        # 서명 변조, 허용되지 않은 alg(none/HS256), 필수 클레임 누락 등 전부 포함.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다") from exc

    roles = claims.get("roles") or []
    if not isinstance(roles, list):
        roles = [str(roles)]
    return TokenPayload(
        sub=str(claims["sub"]),
        aud=str(claims["aud"]),
        exp=int(claims["exp"]),
        roles=[str(r) for r in roles],
        email=str(claims["email"]) if claims.get("email") else None,
        name=str(claims["name"]) if claims.get("name") else None,
        iat=int(claims["iat"]) if "iat" in claims else None,
        jti=str(claims["jti"]) if "jti" in claims else None,
    )


def _extract_token(
    authorization: str | None,
    cookie_token: str | None,
) -> str:
    """Authorization: Bearer <token> 우선, 없으면 access_token 쿠키."""
    if authorization and authorization.strip():
        parts = authorization.strip().split(maxsplit=1)
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
            return parts[1].strip()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="올바르지 않은 토큰 형식입니다")
    if cookie_token and cookie_token.strip():
        return cookie_token.strip()
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 토큰이 필요합니다")


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    access_token: Annotated[str | None, Cookie()] = None,
) -> TokenPayload:
    """헤더 또는 쿠키에서 토큰을 추출·검증하고, jti 즉시차단 목록을 조회한다."""
    token = _extract_token(authorization, access_token)
    payload = verify_token(token, _service_aud())
    await _ensure_not_revoked(payload.jti)
    return payload


_JTI_LOOKUP_TIMEOUT = 0.2  # 검증은 hot path — Redis 지연/장애가 요청을 붙잡지 않도록 상한.


async def _ensure_not_revoked(jti: str | None) -> None:
    """jti가 즉시차단 목록(`authz:jti:block:{jti}`)에 있으면 401.

    Redis 장애·지연 시 fail-open(가용성 우선). 모든 인증 요청이 타는 경로이므로
    짧은 타임아웃으로 감싸 '느린 fail-open'을 막는다.
    """
    if not jti:
        return
    try:
        from matrix.grid_redis_manager import get_redis

        async with asyncio.timeout(_JTI_LOOKUP_TIMEOUT):
            blocked = await get_redis().exists(f"authz:jti:block:{jti}")
    except Exception as exc:
        logger.warning("[seraph] jti 블랙리스트 조회 실패로 fail-open: %s", exc)
        return
    if blocked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="폐기된 토큰입니다")


class RoleChecker:
    """RBAC 가드 — allowed 역할 중 하나라도 보유해야 통과, 아니면 403.

    core는 apps.auth를 import하지 않으므로 역할은 문자열로 받는다
    (apps/auth 측에서 `RoleChecker(Role.ADMIN.value)` 로 호출).
    """

    def __init__(self, *allowed: str) -> None:
        self._allowed = set(allowed)

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not self._allowed & set(user.roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한이 없습니다")
        return user
