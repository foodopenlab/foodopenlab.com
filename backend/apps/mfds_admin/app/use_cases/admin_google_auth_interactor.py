import logging
import os

from mfds_admin.app.dtos.admin_auth_dto import AdminTokenDTO
from mfds_admin.app.exceptions import AdminAuthError, AdminConfigError
from mfds_admin.app.ports.input.admin_google_auth_use_case import AdminGoogleAuthUseCase
from mfds_admin.app.ports.output.admin_repository import AdminRepositoryPort
from mfds_admin.app.use_cases.admin_auth_interactor import create_admin_token

logger = logging.getLogger(__name__)


def _allowed_admin_emails() -> set[str]:
    raw = os.getenv("ADMIN_GOOGLE_EMAILS") or ""
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


class AdminGoogleAuthInteractor(AdminGoogleAuthUseCase):
    def __init__(self, admin_repository: AdminRepositoryPort) -> None:
        self._repo = admin_repository

    async def login_with_google(self, email: str, name: str) -> AdminTokenDTO:
        allowed = _allowed_admin_emails()
        if not allowed:
            logger.error("ADMIN_GOOGLE_EMAILS 미설정 — 구글 어드민 로그인 불가")
            raise AdminConfigError("어드민 구글 허용 목록(ADMIN_GOOGLE_EMAILS)이 설정되지 않았습니다.")

        normalized = email.strip().lower()
        if normalized not in allowed:
            logger.warning("어드민 권한 없는 구글 계정 접근 email=%s", normalized)
            raise AdminAuthError("어드민 권한이 없는 계정입니다.")

        admin = await self._repo.upsert_google_admin(email=normalized, name=name)
        token = create_admin_token(str(admin.id), admin.email)
        minutes = int(os.getenv("ADMIN_JWT_EXPIRE_MINUTES", "120"))
        logger.info("구글 어드민 로그인 성공 admin_id=%s email=%s", admin.id, admin.email)
        return AdminTokenDTO(
            access_token=token,
            token_type="bearer",
            expires_in=minutes * 60,
            admin_name=admin.name,
            admin_id=admin.id,
        )
