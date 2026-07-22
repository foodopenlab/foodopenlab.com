"""apps/auth 테스트 공용 픽스처 — 인메모리 RS256 키페어.

실제 PEM 파일 없이 테스트마다 새 키를 생성해 JWT_PUBLIC_KEY_B64 env에 주입한다.
개인키는 픽스처가 서명용으로만 보유(발급 어댑터 시뮬레이션), 공개키만 검증기에 노출.
"""

from __future__ import annotations

import base64
import time

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

TEST_AUD = "foodopenlab-api"


@pytest.fixture
def rsa_keys():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


@pytest.fixture
def public_key_env(rsa_keys, monkeypatch):
    """검증기가 읽을 JWT_PUBLIC_KEY_B64 를 env에 주입."""
    _, public_pem = rsa_keys
    b64 = base64.b64encode(public_pem.encode()).decode()
    monkeypatch.setenv("JWT_PUBLIC_KEY_B64", b64)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)
    monkeypatch.setenv("SERVICE_AUD", TEST_AUD)
    return public_pem


@pytest.fixture
def private_key_env(rsa_keys, monkeypatch):
    """발급 어댑터가 읽을 JWT_PRIVATE_KEY_B64 를 env에 주입(공개키와 같은 키페어)."""
    private_pem, _ = rsa_keys
    b64 = base64.b64encode(private_pem.encode()).decode()
    monkeypatch.setenv("JWT_PRIVATE_KEY_B64", b64)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    return private_pem


@pytest.fixture
def sign_rs256(rsa_keys):
    """개인키로 RS256 토큰을 서명하는 헬퍼(발급 어댑터 대역)."""
    private_pem, _ = rsa_keys

    def _sign(claims: dict, *, headers: dict | None = None) -> str:
        return jwt.encode(claims, private_pem, algorithm="RS256", headers=headers)

    return _sign


def valid_claims(**overrides) -> dict:
    now = int(time.time())
    base = {
        "sub": "user-123",
        "aud": TEST_AUD,
        "iat": now,
        "exp": now + 600,
        "jti": "jti-abc",
        "roles": ["user"],
    }
    base.update(overrides)
    return base
