"""Phase 5 — RoleChecker 시연: 무토큰 401 · user 403 · admin 200."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import matrix.grid_redis_manager as redis_manager
from auth.adapter.inbound.api.v1.auth_router import router
from auth.adapter.outbound.token.rs256_token_issuer import Rs256TokenIssuer
from auth.tests.fake_redis import FakeRedis


@pytest.fixture
def client(private_key_env, public_key_env, monkeypatch):
    # get_current_user의 jti 블랙리스트 조회가 실제 Redis 연결을 시도하지 않도록 대역 주입.
    monkeypatch.setattr(redis_manager, "get_redis", lambda: FakeRedis())
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _bearer(roles: list[str]) -> dict:
    token = Rs256TokenIssuer().issue_access_token("user-1", roles, "foodopenlab-api").token
    return {"Authorization": f"Bearer {token}"}


def test_no_token_rejected(client):
    assert client.get("/auth/protected-demo").status_code == 401


def test_user_role_forbidden(client):
    r = client.get("/auth/protected-demo", headers=_bearer(["user"]))
    assert r.status_code == 403


def test_admin_role_allowed(client):
    r = client.get("/auth/protected-demo", headers=_bearer(["admin"]))
    assert r.status_code == 200
    assert r.json()["roles"] == ["admin"]
