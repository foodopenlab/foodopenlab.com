from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from matrix.grid_oracle_database_manager import get_db
from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from mfds_user.adapter.outbound.orm.expert_user_orm import ExpertUserORM
from mfds_user.app.services.security import hash_password, verify_password

router = APIRouter(prefix="/mypage", tags=["mypage"])

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

class PasswordUpdateRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

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
        role="expert",  # Returns 'expert' role for expert users
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
        role="expert",
        is_active=True,
        last_login_at=user.last_login.isoformat() if user.last_login else None,
        created_at=user.created_at.isoformat()
    )

@router.patch("/password")
async def update_password(
    req: PasswordUpdateRequest,
    token: UserTokenPayload = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
):
    user_id = UUID(token.sub)
    query = select(ExpertUserORM).where(ExpertUserORM.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    if not user.hashed_password or not verify_password(req.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다."
        )
        
    user.hashed_password = hash_password(req.new_password)
    await session.commit()
    return {"message": "비밀번호가 변경되었습니다"}

@router.delete("/withdraw")
async def withdraw(
    req: PasswordUpdateRequest,  # Frontend sends PasswordUpdateRequest on delete/withdraw too
    token: UserTokenPayload = Depends(verify_token),
    session: AsyncSession = Depends(get_db)
):
    user_id = UUID(token.sub)
    query = select(ExpertUserORM).where(ExpertUserORM.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    if not user.hashed_password or not verify_password(req.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 올바르지 않습니다."
        )
        
    stmt = delete(ExpertUserORM).where(ExpertUserORM.id == user_id)
    await session.execute(stmt)
    await session.commit()
    return {"message": "회원 탈퇴가 완료되었습니다"}
