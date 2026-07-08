import logging
import os
from typing import Annotated

import jwt
from fastapi import Header, HTTPException, Depends
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from matrix.grid_oracle_database_manager import get_db
from mfds_admin.adapter.outbound.orm.admin_orm import AdminORM
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import AdminTokenPayloadSchema

logger = logging.getLogger(__name__)

async def verify_admin_token(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> AdminTokenPayloadSchema:
    if not authorization or not authorization.strip():
        raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")

    parts = authorization.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=401, detail="올바르지 않은 토큰 형식입니다")

    token = parts[1].strip()
    secret = (os.getenv("ADMIN_JWT_SECRET") or "").strip()
    if not secret:
        logger.error("ADMIN_JWT_SECRET 미설정")
        raise HTTPException(status_code=503, detail="Admin 인증 서버 설정이 완료되지 않았습니다.")

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다") from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    if payload.get("role") != "admin":
        logger.warning("Admin 권한 없는 접근 시도 role=%s", payload.get("role"))
        raise HTTPException(status_code=403, detail="Admin 권한이 없습니다")

    # DB에 실제 Admin 계정이 존재하는지 검증 (Stale Token 방지)
    try:
        admin_uuid = UUID(str(payload.get("sub")))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

    stmt = select(AdminORM).where(AdminORM.id == admin_uuid)
    res = await db.execute(stmt)
    admin_row = res.scalar_one_or_none()
    if not admin_row:
        logger.warning("존재하지 않는 Admin ID 접근 시도 sub=%s", payload.get("sub"))
        raise HTTPException(status_code=401, detail="존재하지 않는 관리자 계정입니다. 다시 로그인해 주세요.")

    try:
        return AdminTokenPayloadSchema(
            sub=str(payload["sub"]),
            email=str(payload["email"]),
            role=str(payload["role"]),
            exp=int(payload["exp"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다") from exc

