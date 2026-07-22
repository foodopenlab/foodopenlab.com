"""RS256 발급 어댑터 — 이 파일만이 개인키(JWT_PRIVATE_KEY)를 읽는다 (규칙 4).

개인키는 **호출 시점**에 로드한다 — 모듈 import만으로 키 부재 에러가 나면 안 된다(규칙 5).
검증 컨테이너는 이 어댑터를 import하지 않으므로 개인키 없이도 정상 기동한다.
"""

from __future__ import annotations

import base64
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status

from auth.app.dtos.auth_dto import IssuedAccessToken
from auth.app.ports.output.token_issuer_port import ITokenIssuerPort

_ALGORITHM = "RS256"  # 리터럴 하드코딩 (규칙 3)
_DEFAULT_TTL_MIN = 10
_DEFAULT_KID = "auth-key-1"


class Rs256TokenIssuer(ITokenIssuerPort):
    def issue_access_token(
        self, sub: str, roles: list[str], aud: str, email: str = "", name: str = ""
    ) -> IssuedAccessToken:
        now = datetime.now(timezone.utc)
        ttl_min = int(os.getenv("AUTH_ACCESS_TTL_MIN", str(_DEFAULT_TTL_MIN)))
        expires_at = now + timedelta(minutes=ttl_min)
        jti = uuid.uuid4().hex
        claims = {
            "sub": sub,
            "roles": list(roles),
            "aud": aud,
            "email": email,
            "name": name,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "jti": jti,
        }
        token = jwt.encode(claims, _private_key(), algorithm=_ALGORITHM, headers={"kid": _kid()})
        return IssuedAccessToken(token=token, jti=jti, expires_at=expires_at)


def _private_key() -> str:
    """발급 개인키(PEM)를 호출 시점에 로드. base64 우선, 원문 PEM 폴백."""
    b64 = (os.getenv("JWT_PRIVATE_KEY_B64") or "").strip()
    if b64:
        return base64.b64decode(b64).decode("utf-8")
    raw = (os.getenv("JWT_PRIVATE_KEY") or "").strip()
    if raw:
        return raw
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="발급 개인키(JWT_PRIVATE_KEY)가 설정되지 않았습니다.",
    )


def _kid() -> str:
    return (os.getenv("JWT_KID") or _DEFAULT_KID).strip()
