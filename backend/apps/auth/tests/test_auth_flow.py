"""Phase 4 — OAuth 콜백→발급, 리프레시 로테이션, 로그아웃→jti 블랙리스트, factory, JWKS."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest

from auth.adapter.outbound.oauth.google_oauth_adapter import GoogleOAuthAdapter
from auth.adapter.outbound.oauth.kakao_oauth_adapter import KakaoOAuthAdapter
from auth.adapter.outbound.oauth.naver_oauth_adapter import NaverOAuthAdapter
from auth.adapter.outbound.oauth.oauth_provider_factory import get_oauth_provider
from auth.adapter.outbound.session.redis_oauth_state import RedisOAuthState
from auth.adapter.outbound.session.redis_refresh_session import RedisRefreshSession
from auth.adapter.outbound.token.jwks_provider import build_jwks
from auth.adapter.outbound.token.rs256_token_issuer import Rs256TokenIssuer
from auth.app.dtos.auth_dto import OAuthProfile
from auth.app.ports.output.identity_port import IIdentityPort
from auth.app.use_cases.auth_interactor import AuthInteractor
from auth.domain.entities.auth_identity_entity import AuthIdentity
from auth.domain.exceptions import RefreshReuseError
from auth.tests.conftest import TEST_AUD
from auth.tests.fake_redis import FakeRedis
from matrix.grid_seraph_token_guard_manager import verify_token


class _FakeProvider:
    def __init__(self, provider: str) -> None:
        self.provider = provider

    def authorize_url(self, state: str) -> str:
        return f"https://provider.example/authorize?state={state}"

    async def fetch_profile(self, code: str, state: str) -> OAuthProfile:
        return OAuthProfile(self.provider, "pid-1", "u@example.com", "홍길동")


class _FakeIdentity(IIdentityPort):
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], AuthIdentity] = {}
        self._seq = 0

    async def upsert_oauth_identity(self, profile: OAuthProfile) -> AuthIdentity:
        from auth.domain.value_objects.role import resolve_roles_for_email

        roles = resolve_roles_for_email(profile.email)  # 테스트 대역은 admin/user만(expert는 DB)
        key = (profile.provider, profile.provider_id)
        if key not in self._store:
            self._seq += 1
            self._store[key] = AuthIdentity(
                id=self._seq, provider=profile.provider, provider_id=profile.provider_id,
                email=profile.email, name=profile.name, roles=roles,
            )
        else:
            self._store[key].roles = roles
        return self._store[key]

    async def get(self, identity_id: str) -> AuthIdentity | None:
        for ident in self._store.values():
            if str(ident.id) == str(identity_id):
                return ident
        return None


@pytest.fixture
def interactor(private_key_env, public_key_env):
    redis = FakeRedis()
    return AuthInteractor(
        provider_factory=_FakeProvider,
        identity=_FakeIdentity(),
        token_issuer=Rs256TokenIssuer(),
        refresh_session=RedisRefreshSession(redis),
        state_store=RedisOAuthState(redis),
    )


async def _login(interactor, provider="google"):
    url = await interactor.build_authorize_url(provider)
    state = parse_qs(urlparse(url).query)["state"][0]
    return await interactor.handle_callback(provider, "auth-code", state)


async def test_callback_issues_verifiable_tokens(interactor):
    bundle = await _login(interactor)
    payload = verify_token(bundle.access_token, TEST_AUD)  # 공개키 검증 통과
    assert payload.sub == bundle.sub
    assert payload.roles == ["user"]
    assert payload.email == "u@example.com"  # 토큰에 email 실림(백엔드 유저 라우트용)
    assert bundle.refresh_token
    assert bundle.expires_in > 0


async def test_admin_whitelist_assigns_admin_role(interactor, monkeypatch):
    monkeypatch.setenv("ADMIN_GOOGLE_EMAILS", "u@example.com, boss@foodopenlab.com")
    bundle = await _login(interactor)  # _FakeProvider 이메일이 u@example.com
    payload = verify_token(bundle.access_token, TEST_AUD)
    assert "admin" in payload.roles


async def test_non_whitelisted_email_is_user(interactor, monkeypatch):
    monkeypatch.setenv("ADMIN_GOOGLE_EMAILS", "someone-else@foodopenlab.com")
    bundle = await _login(interactor)
    payload = verify_token(bundle.access_token, TEST_AUD)
    assert payload.roles == ["user"]


async def test_callback_rejects_forged_state(interactor):
    with pytest.raises(ValueError):
        await interactor.handle_callback("google", "code", "never-issued-state")


async def test_refresh_rotates_and_reuse_is_detected(interactor):
    bundle = await _login(interactor)
    rotated = await interactor.refresh(bundle.refresh_token)
    assert rotated.refresh_token != bundle.refresh_token
    verify_token(rotated.access_token, TEST_AUD)
    # 옛 refresh 재사용 → 감지
    with pytest.raises(RefreshReuseError):
        await interactor.refresh(bundle.refresh_token)


async def test_logout_blacklists_jti(interactor):
    bundle = await _login(interactor)
    payload = verify_token(bundle.access_token, TEST_AUD)
    await interactor.logout(payload, bundle.refresh_token)
    assert await interactor._refresh.is_jti_blacklisted(payload.jti) is True


def test_provider_factory_resolves_all_three():
    assert isinstance(get_oauth_provider("google"), GoogleOAuthAdapter)
    assert isinstance(get_oauth_provider("kakao"), KakaoOAuthAdapter)
    assert isinstance(get_oauth_provider("naver"), NaverOAuthAdapter)


def test_provider_factory_rejects_unknown():
    with pytest.raises(ValueError):
        get_oauth_provider("myspace")


def test_jwks_exposes_public_key(private_key_env, monkeypatch):
    monkeypatch.setenv("JWT_KID", "kid-99")
    jwks = build_jwks()
    assert len(jwks["keys"]) == 1
    key = jwks["keys"][0]
    assert key["kty"] == "RSA"
    assert key["kid"] == "kid-99"
    assert key["use"] == "sig"
    assert "d" not in key  # 개인키 파라미터 미포함
