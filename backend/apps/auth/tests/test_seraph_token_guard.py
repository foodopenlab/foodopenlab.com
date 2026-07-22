"""Phase 1 AC — RS256 검증기 거부 케이스.

만료 · 서명변조 · alg=none · alg=HS256 강제 · aud 불일치 전부 거부하고,
정상 토큰은 공개키만으로 검증 통과함을 보장한다.
"""

from __future__ import annotations

import time

import jwt
import pytest
from fastapi import HTTPException

from matrix.grid_seraph_token_guard_manager import RoleChecker, TokenPayload, verify_token
from auth.tests.conftest import TEST_AUD, valid_claims


def test_valid_token_roundtrip(public_key_env, sign_rs256):
    """발급→공개키 검증 왕복: 개인키로 서명한 토큰을 공개키로 검증 통과."""
    token = sign_rs256(valid_claims(), headers={"kid": "k1"})
    payload = verify_token(token, TEST_AUD)
    assert isinstance(payload, TokenPayload)
    assert payload.sub == "user-123"
    assert payload.roles == ["user"]
    assert payload.jti == "jti-abc"


def test_expired_token_rejected(public_key_env, sign_rs256):
    token = sign_rs256(valid_claims(exp=int(time.time()) - 10))
    with pytest.raises(HTTPException) as exc:
        verify_token(token, TEST_AUD)
    assert exc.value.status_code == 401


def test_tampered_signature_rejected(public_key_env, sign_rs256):
    token = sign_rs256(valid_claims())
    # payload 세그먼트 한 글자 변조 → 서명 불일치
    head, body, sig = token.split(".")
    tampered = f"{head}.{body[:-2] + ('AA' if body[-2:] != 'AA' else 'BB')}.{sig}"
    with pytest.raises(HTTPException) as exc:
        verify_token(tampered, TEST_AUD)
    assert exc.value.status_code == 401


def test_alg_none_rejected(public_key_env):
    """alg=none 강제(서명 없는) 토큰 거부 — 알고리즘 화이트리스트."""
    token = jwt.encode(valid_claims(), key=None, algorithm="none")
    with pytest.raises(HTTPException) as exc:
        verify_token(token, TEST_AUD)
    assert exc.value.status_code == 401


def test_alg_hs256_forced_rejected(public_key_env):
    """alg=HS256 토큰 거부 — 알고리즘 화이트리스트(["RS256"])가 혼동 공격을 차단.

    (PyJWT는 공개키를 HMAC 시크릿으로 쓰는 걸 encode 단계에서도 막지만, 우리 방어선은
    decode의 algorithms=["RS256"]이다. 임의 시크릿 HS256 토큰도 alg 불일치로 거부돼야 한다.)
    """
    token = jwt.encode(valid_claims(), "attacker-chosen-secret", algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        verify_token(token, TEST_AUD)
    assert exc.value.status_code == 401


def test_wrong_audience_rejected(public_key_env, sign_rs256):
    token = sign_rs256(valid_claims(aud="other-service-api"))
    with pytest.raises(HTTPException) as exc:
        verify_token(token, TEST_AUD)
    assert exc.value.status_code == 403


def test_role_checker_allows_matching_role():
    guard = RoleChecker("admin")
    user = TokenPayload(sub="a", aud=TEST_AUD, exp=0, roles=["admin"])
    assert guard(user) is user


def test_role_checker_rejects_missing_role():
    guard = RoleChecker("admin")
    user = TokenPayload(sub="a", aud=TEST_AUD, exp=0, roles=["user"])
    with pytest.raises(HTTPException) as exc:
        guard(user)
    assert exc.value.status_code == 403
