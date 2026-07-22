"""유저 토큰 검증 — auth(RS256) 통합. 시그니처·UserTokenPayload는 유지해 라우터 무변경.

기존 HS256(token_service) 대신 core seraph 검증기(공개키)를 쓴다.
roles(list) → 단일 role 문자열로 매핑(admin 우선).
"""

from fastapi import Depends
from pydantic import BaseModel

from matrix.grid_seraph_token_guard_manager import TokenPayload, get_current_user


class UserTokenPayload(BaseModel):
    sub: str
    email: str
    role: str
    exp: int


def _primary_role(roles: list[str]) -> str:
    if "admin" in roles:
        return "admin"
    return roles[0] if roles else "user"


async def verify_token(user: TokenPayload = Depends(get_current_user)) -> UserTokenPayload:
    return UserTokenPayload(
        sub=user.sub,
        email=user.email or "",
        role=_primary_role(user.roles),
        exp=user.exp,
    )
