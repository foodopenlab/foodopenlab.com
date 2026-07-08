from typing import Optional

from pydantic import BaseModel, Field


class AdminLoginRequestSchema(BaseModel):
    email: str = Field(..., min_length=1, description="관리자 이메일")
    password: str = Field(..., min_length=1, description="비밀번호")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "password": "secure-password",
            }
        }
    }


class AdminTokenResponseSchema(BaseModel):
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료까지 남은 시간(초)")
    admin_name: str = Field(..., description="관리자 표시 이름")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "admin_name": "시스템 관리자",
            }
        }
    }


class AdminTokenPayloadSchema(BaseModel):
    sub: str = Field(..., description="관리자 UUID")
    email: str = Field(..., description="이메일")
    role: str = Field(..., description="역할")
    exp: int = Field(..., description="만료 시각 (Unix timestamp)")
