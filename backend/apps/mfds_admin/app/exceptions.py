"""mfds_admin 애플리케이션 예외 — HTTP는 라우터에서 변환한다(레이어 경계 유지)."""


class AdminAuthError(Exception):
    """관리자 인증 실패 — 이메일/비밀번호 불일치 (라우터에서 401로 변환)."""


class AdminConfigError(Exception):
    """관리자 인증 서버 설정 누락 — ADMIN_JWT_SECRET 등 (라우터에서 503으로 변환)."""
