import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import TypedDict
from uuid import UUID

USER_JWT_SECRET = (
    os.getenv("USER_JWT_SECRET") 
    or os.getenv("ADMIN_JWT_SECRET") 
    or "haccp_user_default_secret_key_2026_default"
).strip()

USER_JWT_EXPIRE_MINUTES = int(os.getenv("USER_JWT_EXPIRE_MINUTES", "120"))

class TokenPayload(TypedDict):
    sub: str
    email: str
    role: str
    exp: int

def generate_access_token(user_id: UUID, email: str, role: str) -> tuple[str, datetime]:
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(minutes=USER_JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": int(expires_at.timestamp())
    }
    token = jwt.encode(payload, USER_JWT_SECRET, algorithm="HS256")
    return token, expires_at.replace(tzinfo=None)

def decode_access_token(token: str) -> TokenPayload:
    payload = jwt.decode(token, USER_JWT_SECRET, algorithms=["HS256"])
    return {
        "sub": str(payload["sub"]),
        "email": str(payload["email"]),
        "role": str(payload["role"]),
        "exp": int(payload["exp"])
    }
