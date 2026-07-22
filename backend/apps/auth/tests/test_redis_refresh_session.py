"""Phase 3 AC — refresh 로테이션 + 재사용 감지(세션 전체 폐기) + jti 블랙리스트."""

from __future__ import annotations

import pytest

from auth.adapter.outbound.session.redis_refresh_session import RedisRefreshSession
from auth.domain.exceptions import InvalidRefreshError, RefreshReuseError
from auth.tests.fake_redis import FakeRedis


@pytest.fixture
def session():
    return RedisRefreshSession(FakeRedis())


async def test_rotate_issues_new_and_invalidates_old(session):
    t0 = await session.start("user-1")
    rot = await session.rotate(t0)
    assert rot.sub == "user-1"
    assert rot.refresh_token != t0
    # 새 토큰은 다시 로테이션 가능
    rot2 = await session.rotate(rot.refresh_token)
    assert rot2.sub == "user-1"


async def test_unknown_token_rejected(session):
    with pytest.raises(InvalidRefreshError):
        await session.rotate("does-not-exist")


async def test_reuse_detection_revokes_all_sessions(session):
    # 같은 사용자의 두 세션(예: 기기 2대)
    device_a = await session.start("user-1")
    device_b = await session.start("user-1")

    # A를 정상 로테이션 → device_a 는 이제 'used'
    rot_a = await session.rotate(device_a)

    # 탈취된 옛 토큰(device_a) 재사용 → 재사용 감지
    with pytest.raises(RefreshReuseError):
        await session.rotate(device_a)

    # sub 전체 폐기: A의 새 토큰도, 무관했던 B도 전부 무효
    with pytest.raises(InvalidRefreshError):
        await session.rotate(rot_a.refresh_token)
    with pytest.raises(InvalidRefreshError):
        await session.rotate(device_b)


async def test_revoke_single_token(session):
    t0 = await session.start("user-1")
    await session.revoke(t0)
    with pytest.raises(InvalidRefreshError):
        await session.rotate(t0)


async def test_jti_blacklist(session):
    assert await session.is_jti_blacklisted("jti-x") is False
    await session.blacklist_jti("jti-x", ttl_seconds=60)
    assert await session.is_jti_blacklisted("jti-x") is True
