from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MemberDTO:
    """가입 회원 + 승격(화이트리스트) 여부."""

    id: str
    email: str
    name: str | None
    auth_provider: str          # 'email' | 'google' | 'kakao' | 'naver'
    is_expert: bool             # 화이트리스트 승격 여부
    last_login: datetime | None
    created_at: datetime
