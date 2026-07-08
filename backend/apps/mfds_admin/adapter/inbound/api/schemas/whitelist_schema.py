from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddWhitelistRequest(BaseModel):
    email: str = Field(..., min_length=1, description="초대할 전문가 이메일")
    invited_name: Optional[str] = Field(default=None, description="초대 대상 이름")
    role_desc: Optional[str] = Field(default=None, description="역할 설명")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "expert@example.com",
                "invited_name": "홍길동",
                "role_desc": "식품안전 전문가",
            }
        }
    }


class WhitelistResponse(BaseModel):
    email: str = Field(..., description="화이트리스트 이메일")
    invited_name: Optional[str] = Field(default=None, description="초대 대상 이름")
    role_desc: Optional[str] = Field(default=None, description="역할 설명")
    added_by: str = Field(..., description="등록 관리자 UUID")
    added_at: datetime = Field(..., description="등록 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "expert@example.com",
                "invited_name": "홍길동",
                "role_desc": "식품안전 전문가",
                "added_by": "550e8400-e29b-41d4-a716-446655440000",
                "added_at": "2026-06-15T10:00:00",
            }
        }
    }
