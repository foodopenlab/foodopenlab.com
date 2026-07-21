from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from matrix.grid_oracle_database_manager import get_db
from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from matrix.orm.expert_user_orm import ExpertUserORM
from matrix.orm.expert_whitelist_orm import ExpertWhitelistORM

router = APIRouter(prefix="/mypage", tags=["mypage"])


async def _resolve_role(session: AsyncSession, email: str) -> str:
    """전문가 여부는 화이트리스트(관리자 승격) 등재 여부로 판정 — 없으면 일반(general)."""
    query = select(ExpertWhitelistORM.email).where(ExpertWhitelistORM.email == email)
    promoted = (await session.execute(query)).scalar_one_or_none()
    return "expert" if promoted else "general"

class ProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool = True
    last_login_at: Optional[str] = None
    created_at: str

class ProfileUpdateRequest(BaseModel):
    name: str

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    token: UserTokenPayload = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    user_id = UUID(token.sub)
    query = select(ExpertUserORM).where(ExpertUserORM.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    return ProfileResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=await _resolve_role(session, user.email),
        is_active=True,
        last_login_at=user.last_login.isoformat() if user.last_login else None,
        created_at=user.created_at.isoformat()
    )

@router.patch("/profile", response_model=ProfileResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    token: UserTokenPayload = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
) -> ProfileResponse:
    user_id = UUID(token.sub)
    query = select(ExpertUserORM).where(ExpertUserORM.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    user.name = req.name.strip()
    await session.commit()
    await session.refresh(user)
    
    return ProfileResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=await _resolve_role(session, user.email),
        is_active=True,
        last_login_at=user.last_login.isoformat() if user.last_login else None,
        created_at=user.created_at.isoformat()
    )

@router.delete("/withdraw")
async def withdraw(
    token: UserTokenPayload = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
):
    # 소셜 전용 가입이므로 비밀번호가 없다 — 인증 토큰만으로 탈퇴 처리한다.
    user_id = UUID(token.sub)
    query = select(ExpertUserORM).where(ExpertUserORM.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    stmt = delete(ExpertUserORM).where(ExpertUserORM.id == user_id)
    await session.execute(stmt)
    await session.commit()
    return {"message": "회원 탈퇴가 완료되었습니다"}
