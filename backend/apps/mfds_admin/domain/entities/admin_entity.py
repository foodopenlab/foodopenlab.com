from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Admin:
    """관리자 계정 애그리게이트 — 인증 자격증명(해시)을 포함한다."""

    id: UUID
    email: str
    name: str
    hashed_password: str
    last_login: Optional[datetime] = None
