from typing import Annotated
from fastapi import Header, HTTPException, status
from pydantic import BaseModel
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from mfds_user.app.services.token_service import decode_access_token

class UserTokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int

async def verify_token(
    authorization: Annotated[str | None, Header()] = None,
) -> UserTokenPayload:
    if not authorization or not authorization.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다"
        )

    parts = authorization.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="올바르지 않은 토큰 형식입니다"
        )

    token = parts[1].strip()
    try:
        payload = decode_access_token(token)
        return UserTokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            role=payload["role"],
            exp=payload["exp"]
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다"
        ) from exc
    except (InvalidTokenError, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다"
        ) from exc
