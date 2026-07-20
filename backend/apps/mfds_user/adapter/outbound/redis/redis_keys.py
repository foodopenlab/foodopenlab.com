"""mfds_user Redis 키 컨벤션(SSOT) — colon 네임스페이스."""

# 발급된 세션(JWT access/refresh) 저장 — access_token / refresh_token 각각으로 조회
SESSION_BY_ACCESS = "mfds:user:session:access:{access_token}"
SESSION_BY_REFRESH = "mfds:user:session:refresh:{refresh_token}"
# 유저별 활성 refresh_token 집합 (전체 로그아웃·감사용)
USER_SESSIONS = "mfds:user:sessions:{user_id}"
# OAuth CSRF state (login→callback 사이 단기 보관)
OAUTH_STATE = "mfds:user:oauth:state:{state}"
