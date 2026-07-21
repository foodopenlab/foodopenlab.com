"""시스템 전역 비밀번호 해싱·검증(PBKDF2-HMAC-SHA256)을 한곳에서 관리합니다.

BC(mfds_user·mfds_admin 등)가 공유하는 전역 인프라 — 특정 앱에 두면 Spoke↔Spoke
참조가 되므로 core/에 위치한다.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, digest_hex = stored_hash.split("$", 1)
    if not salt or len(digest_hex) != 64:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(digest.hex(), digest_hex)
