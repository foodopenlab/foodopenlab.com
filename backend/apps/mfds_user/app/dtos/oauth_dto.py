from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthProfile:
    """소셜 제공사에서 정규화한 사용자 프로필."""

    provider: str          # 'google' | 'kakao' | 'naver'
    provider_id: str       # 제공사 고유 subject (sub / id)
    email: str             # 없으면 상위에서 합성 이메일로 채워 넣는다
    name: str
    picture: str | None
