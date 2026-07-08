from typing import Literal

from pydantic import BaseModel, Field

SignupPublicRole = Literal["expert"]


class SignupRequest(BaseModel):
    email: str = Field(..., description="가입 이메일")
    password: str = Field(..., description="비밀번호")
    name: str = Field(..., description="표시 이름")
    agreed: bool = Field(..., description="약관 동의 여부")
    role: SignupPublicRole = Field(
        default="expert",
        description="전문가 회원 가입",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "expert@example.com",
                "password": "secure-password",
                "name": "홍길동",
                "agreed": True,
                "role": "expert",
            }
        }
    }


class SignupResponse(BaseModel):
    ok: bool = Field(True, description="가입 성공 여부")
    message: str = Field("회원가입이 완료되었습니다.", description="결과 메시지")
    user_id: str = Field(..., description="사용자 UUID")
    email: str = Field(..., description="가입 이메일")
    name: str = Field(..., description="표시 이름")
    role: SignupPublicRole = Field(..., description="가입 역할")
    access_token: str = Field(..., description="JWT 액세스 토큰 (가입 즉시 자동 로그인용)")
    token_type: str = Field("bearer", description="토큰 타입")

    model_config = {
        "json_schema_extra": {
            "example": {
                "ok": True,
                "message": "회원가입이 완료되었습니다.",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "expert@example.com",
                "name": "홍길동",
                "role": "expert",
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class LoginRequest(BaseModel):
    email: str = Field(..., description="로그인 이메일")
    password: str = Field(..., description="비밀번호")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "expert@example.com",
                "password": "secure-password",
            }
        }
    }


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")
    user_id: str = Field(..., description="사용자 UUID")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="표시 이름")
    role: str = Field(..., description="역할")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "expert@example.com",
                "name": "홍길동",
                "role": "expert",
            }
        }
    }
