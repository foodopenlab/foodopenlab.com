"""RBAC 역할 — auth BC 도메인 정책 (원본 rbac.py 대응).

Permission 매핑은 Phase 5에서 확장한다. core `RoleChecker`는 문자열을 받으므로
호출부에서 `Role.ADMIN.value` 형태로 전달한다.
"""

from __future__ import annotations

import os
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


DEFAULT_ROLE = Role.USER


def _admin_whitelist() -> set[str]:
    """ADMIN_GOOGLE_EMAILS(콤마 목록) → 소문자 집합. (mfds_admin과 동일 규약)"""
    raw = os.getenv("ADMIN_GOOGLE_EMAILS") or ""
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def resolve_roles_for_email(email: str) -> list[str]:
    """이메일이 어드민 화이트리스트에 있으면 admin, 아니면 user 역할을 부여한다.

    로그인마다 재평가하므로 화이트리스트 변경이 다음 로그인에 반영된다.
    """
    if email and email.strip().lower() in _admin_whitelist():
        return [Role.ADMIN.value, Role.USER.value]
    return [Role.USER.value]
