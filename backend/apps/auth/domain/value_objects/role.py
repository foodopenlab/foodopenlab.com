"""RBAC 역할 — auth BC 도메인 정책 (원본 rbac.py 대응).

Permission 매핑은 Phase 5에서 확장한다. core `RoleChecker`는 문자열을 받으므로
호출부에서 `Role.ADMIN.value` 형태로 전달한다.
"""

from __future__ import annotations

import os
from enum import Enum


class Role(str, Enum):
    USER = "user"
    EXPERT = "expert"
    ADMIN = "admin"


DEFAULT_ROLE = Role.USER


def _admin_whitelist() -> set[str]:
    """ADMIN_GOOGLE_EMAILS(콤마 목록) → 소문자 집합. (mfds_admin과 동일 규약)"""
    raw = os.getenv("ADMIN_GOOGLE_EMAILS") or ""
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def is_admin_email(email: str) -> bool:
    return bool(email) and email.strip().lower() in _admin_whitelist()


def resolve_roles_for_email(email: str) -> list[str]:
    """DB 없이 판정 가능한 admin/user만 결정(fallback용).

    expert 판정은 DB(expert_whitelist)가 필요하므로 저장소(repository)에서 수행한다.
    우선순위: admin > expert > user.
    """
    if is_admin_email(email):
        return [Role.ADMIN.value, Role.USER.value]
    return [Role.USER.value]
