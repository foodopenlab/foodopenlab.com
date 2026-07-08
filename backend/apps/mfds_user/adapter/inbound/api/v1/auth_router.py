from fastapi import APIRouter, Depends, HTTPException, Header, status
from typing import Annotated, cast
from mfds_user.app.ports.input.auth_use_case import AuthUseCase
from mfds_user.dependencies.auth import get_auth_use_case
from mfds_user.adapter.inbound.api.schemas.auth_schema import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    SignupPublicRole
)
from mfds_user.app.mappers.auth_mapper import to_signup_command, to_login_command

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    req: SignupRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
) -> SignupResponse:
    try:
        command = to_signup_command(req)
        session = await use_case.signup(command)
        return SignupResponse(
            ok=True,
            message="회원가입이 완료되었습니다.",
            user_id=str(session.user_id),
            email=session.email,
            name=session.name,
            role=cast(SignupPublicRole, session.role),
            access_token=session.access_token,
            token_type="bearer"
        )
    except ValueError as e:
        err_msg = str(e)
        if "이미 등록된 이메일입니다" in err_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err_msg)
        elif "가입 승인 대상" in err_msg:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=err_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

@router.post("/login", response_model=LoginResponse)
async def login(
    req: LoginRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case)
) -> LoginResponse:
    try:
        command = to_login_command(req)
        session = await use_case.login(command)
        return LoginResponse(
            access_token=session.access_token,
            token_type="bearer",
            user_id=str(session.user_id),
            email=session.email,
            name=session.name,
            role=session.role
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=LoginResponse)
async def refresh(
    refresh_token: str,
    use_case: AuthUseCase = Depends(get_auth_use_case)
) -> LoginResponse:
    try:
        session = await use_case.refresh_token(refresh_token)
        return LoginResponse(
            access_token=session.access_token,
            token_type="bearer",
            user_id=str(session.user_id),
            email=session.email,
            name=session.name,
            role=session.role
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    authorization: Annotated[str | None, Header()] = None,
    use_case: AuthUseCase = Depends(get_auth_use_case)
) -> None:
    if not authorization or not authorization.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 토큰이 필요합니다")
    
    parts = authorization.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="올바르지 않은 토큰 형식입니다")
    
    token = parts[1].strip()
    await use_case.logout(token)
