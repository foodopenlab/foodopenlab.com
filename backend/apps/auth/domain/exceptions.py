"""auth BC 도메인 예외."""

from __future__ import annotations


class AuthError(Exception):
    """auth 도메인 기반 예외."""


class InvalidRefreshError(AuthError):
    """존재하지 않거나 이미 만료된 refresh 토큰."""


class RefreshReuseError(AuthError):
    """이미 로테이션된(사용 완료) refresh 토큰 재사용 감지 — 세션 전체 폐기됨."""
