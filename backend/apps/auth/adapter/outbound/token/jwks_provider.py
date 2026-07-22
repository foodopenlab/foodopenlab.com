"""JWKS 제공 — 공개키를 JWK(kid 포함)로 노출. 외부/백엔드 검증자가 사용.

공개키는 env(JWT_PUBLIC_KEY[_B64])에서 읽고, 없으면 개인키에서 파생한다.
개인키 원문은 반환하지 않는다(공개 파라미터만).
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from fastapi import HTTPException, status
from jwt.algorithms import RSAAlgorithm

_DEFAULT_KID = "auth-key-1"


def _kid() -> str:
    return (os.getenv("JWT_KID") or _DEFAULT_KID).strip()


def _env_pem(name: str) -> str | None:
    b64 = (os.getenv(f"{name}_B64") or "").strip()
    if b64:
        return base64.b64decode(b64).decode("utf-8")
    raw = (os.getenv(name) or "").strip()
    return raw or None


def _public_key() -> RSAPublicKey:
    pub_pem = _env_pem("JWT_PUBLIC_KEY")
    if pub_pem:
        return serialization.load_pem_public_key(pub_pem.encode())
    priv_pem = _env_pem("JWT_PRIVATE_KEY")
    if priv_pem:
        return serialization.load_pem_private_key(priv_pem.encode(), password=None).public_key()
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="JWKS를 만들 공개키가 없습니다 (JWT_PUBLIC_KEY 또는 JWT_PRIVATE_KEY).",
    )


def build_jwks() -> dict:
    jwk = RSAAlgorithm.to_jwk(_public_key(), as_dict=True)
    jwk.update({"kid": _kid(), "use": "sig", "alg": "RS256"})
    return {"keys": [jwk]}
