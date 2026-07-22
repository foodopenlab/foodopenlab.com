"""Phase 2 AC — 발급→공개키 검증 왕복 · import 시 키 부재 무해."""

from __future__ import annotations

import importlib

import jwt

from matrix.grid_seraph_token_guard_manager import verify_token
from auth.adapter.outbound.token.rs256_token_issuer import Rs256TokenIssuer
from auth.tests.conftest import TEST_AUD


def test_issue_then_verify_roundtrip(private_key_env, public_key_env):
    issued = Rs256TokenIssuer().issue_access_token("user-9", ["user", "admin"], TEST_AUD)
    # 발급된 토큰을 공개키만으로 검증 통과
    payload = verify_token(issued.token, TEST_AUD)
    assert payload.sub == "user-9"
    assert payload.roles == ["user", "admin"]
    assert payload.jti == issued.jti


def test_issued_token_has_kid_header(private_key_env, monkeypatch):
    monkeypatch.setenv("JWT_KID", "test-kid-42")
    issued = Rs256TokenIssuer().issue_access_token("u", ["user"], TEST_AUD)
    header = jwt.get_unverified_header(issued.token)
    assert header["kid"] == "test-kid-42"
    assert header["alg"] == "RS256"


def test_module_import_without_private_key_is_safe(monkeypatch):
    """개인키 없이 모듈 import만으로 에러가 나면 안 된다(규칙 5)."""
    monkeypatch.delenv("JWT_PRIVATE_KEY_B64", raising=False)
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    module = importlib.import_module("auth.adapter.outbound.token.rs256_token_issuer")
    importlib.reload(module)  # 재로딩해도 키 접근 없음
    assert hasattr(module, "Rs256TokenIssuer")
