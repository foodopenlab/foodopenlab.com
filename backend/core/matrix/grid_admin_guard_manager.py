"""Admin RBAC 가드 — auth(RS256) 통합. 시그니처는 유지해 라우터 무변경.

기존 HS256(ADMIN_JWT_SECRET) 대신 core seraph 검증기(공개키)를 쓰고,
roles 클레임에 'admin'이 있는지로 RBAC를 판정한다.
"""

import os

from fastapi import Depends, HTTPException

from matrix.grid_seraph_token_guard_manager import (
    TokenPayload,
    get_current_user,
    verify_token as _seraph_verify,
)


def _aud() -> str:
    return (os.getenv("SERVICE_AUD") or "foodopenlab-api").strip()


def decode_admin_jwt(token: str) -> dict:
    """RS256 검증 + roles에 admin 포함 확인 후 payload(dict) 반환. RBAC 단일 지점.

    (raw 토큰 문자열용 — 예: /docs 쿠키 검증. 유효하지 않으면 HTTPException.)
    """
    payload = _seraph_verify(token, _aud())  # 만료·서명·aud 검증(HTTPException on 실패)
    if "admin" not in payload.roles:
        raise HTTPException(status_code=403, detail="Admin 권한이 없습니다")
    return {"sub": payload.sub, "roles": payload.roles, "email": payload.email, "role": "admin"}


async def verify_admin_jwt(user: TokenPayload = Depends(get_current_user)) -> str:
    """헤더/쿠키 토큰 기반 admin RBAC 가드 → sub 반환."""
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Admin 권한이 없습니다")
    return str(user.sub)
