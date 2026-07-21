import os
import logging
from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional
from mfds_admin.app.ports.input.admin_auth_use_case import AdminAuthUseCase
from mfds_admin.app.ports.output.admin_repository import AdminRepositoryPort
from mfds_admin.app.dtos.admin_auth_dto import AdminLoginCommand, AdminTokenDTO
from mfds_admin.app.exceptions import AdminAuthError, AdminConfigError
from matrix.grid_cypher_password_manager import verify_password

logger = logging.getLogger(__name__)

def create_admin_token(user_id: str, email: str) -> str:
    secret = (os.getenv("ADMIN_JWT_SECRET") or "").strip()
    if not secret:
        raise ValueError("ADMIN_JWT_SECRET 미설정")
    minutes = int(os.getenv("ADMIN_JWT_EXPIRE_MINUTES", "120"))
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "role": "admin",
        "exp": exp,
    }
    return jwt.encode(payload, secret, algorithm="HS256")

class AdminAuthInteractor(AdminAuthUseCase):
    def __init__(self, admin_repository: AdminRepositoryPort) -> None:
        self._repo = admin_repository

    async def login(self, command: AdminLoginCommand) -> AdminTokenDTO:
        if not (os.getenv("ADMIN_JWT_SECRET") or "").strip():
            logger.error("ADMIN_JWT_SECRET 미설정 — Admin 로그인 불가")
            raise AdminConfigError("Admin JWT 서버 설정(ADMIN_JWT_SECRET)이 필요합니다.")

        user = await self._repo.get_admin_by_email(command.email)
        if user is None:
            logger.warning("Admin 로그인 실패 — 계정 없음 email=%s", command.email)
            raise AdminAuthError("이메일 또는 비밀번호가 올바르지 않습니다")

        if not verify_password(command.password, user.hashed_password):
            logger.warning("Admin 로그인 실패 — 비밀번호 불일치 email=%s", command.email)
            raise AdminAuthError("이메일 또는 비밀번호가 올바르지 않습니다")

        token = create_admin_token(str(user.id), user.email)
        await self._repo.update_last_login(user.id)

        minutes = int(os.getenv("ADMIN_JWT_EXPIRE_MINUTES", "120"))
        expires_in = minutes * 60

        logger.info("Admin 로그인 성공 user_id=%s email=%s", user.id, user.email)
        return AdminTokenDTO(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            admin_name=user.name,
            admin_id=user.id
        )
