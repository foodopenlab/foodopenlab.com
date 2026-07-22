"""Admin 토큰 검증 — auth(RS256) 통합. AdminTokenPayloadSchema는 유지해 라우터 무변경.

기존 HS256(ADMIN_JWT_SECRET) + AdminORM 존재검증 대신, core seraph(공개키)로
RS256 검증하고 roles에 'admin'이 있는지로 판정한다. admin 여부의 원천은
auth의 화이트리스트(ADMIN_GOOGLE_EMAILS)이므로 별도 AdminORM 조회는 불필요.
"""

from fastapi import Depends, HTTPException

from matrix.grid_seraph_token_guard_manager import TokenPayload, get_current_user
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import AdminTokenPayloadSchema


async def verify_admin_token(
    user: TokenPayload = Depends(get_current_user),
) -> AdminTokenPayloadSchema:
    if "admin" not in user.roles:
        raise HTTPException(status_code=403, detail="Admin 권한이 없습니다")
    return AdminTokenPayloadSchema(
        sub=user.sub,
        email=user.email or "",
        role="admin",
        exp=user.exp,
    )
