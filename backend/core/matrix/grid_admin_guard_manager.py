import os
from typing import Annotated

import jwt
from fastapi import Header, HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def decode_admin_jwt(token: str) -> dict:
    """Admin JWT 서명·만료·role(=admin) 검증 후 payload 반환.

    RBAC 판정의 단일 지점. 유효하지 않으면 HTTPException을 던진다.
    (DB 계정 존재 확인은 mfds_admin 소관 — apps 간 직접 참조 방지.)
    """
    secret = (os.getenv("ADMIN_JWT_SECRET") or "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="Admin 인증 서버 설정이 완료되지 않았습니다.")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다") from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin 권한이 없습니다")
    return payload


async def verify_admin_jwt(authorization: Annotated[str | None, Header()] = None) -> str:
    """Authorization: Bearer <admin JWT> 헤더 기반 RBAC 가드 → sub 반환."""
    if not authorization or not authorization.strip():
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")

    parts = authorization.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=401, detail="올바르지 않은 토큰 형식입니다")

    payload = decode_admin_jwt(parts[1].strip())
    return str(payload.get("sub", ""))
