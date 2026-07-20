from datetime import datetime, timedelta
import secrets
from uuid import UUID
from mfds_user.app.ports.input.auth_use_case import AuthUseCase
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.app.dtos.auth_dto import SignupCommand, LoginCommand, UserSessionDTO
from mfds_user.app.services.security import hash_password, verify_password
from mfds_user.app.services.token_service import generate_access_token

class AuthInteractor(AuthUseCase):
    def __init__(self, auth_repository: AuthRepository) -> None:
        self._auth_repository = auth_repository

    async def _resolve_role(self, email: str) -> str:
        """역할은 화이트리스트 승격 여부로 결정 — 승격되면 expert, 아니면 general."""
        whitelist_entry = await self._auth_repository.find_whitelisted_email(email)
        return "expert" if whitelist_entry else "general"

    async def signup(self, command: SignupCommand) -> UserSessionDTO:
        email = command.email.strip()
        if "@" not in email:
            raise ValueError("업무용 이메일 주소에 @가 포함된 올바른 형식을 입력해 주세요.")
        if not command.agreed:
            raise ValueError("이용약관 및 개인정보처리방침에 동의해 주세요.")

        # 1. 이메일 중복 확인 (화이트리스트 사전 승인 게이트는 폐지 — 누구나 가입, 이후 관리자 승격)
        existing_user = await self._auth_repository.find_user_by_email(email)
        if existing_user:
            raise ValueError("이미 등록된 이메일입니다.")

        # 2. 역할 결정 (신규 가입자는 보통 general, 이미 화이트리스트면 expert)
        role = await self._resolve_role(email)

        # 3. 사용자 저장 (expert_users 테이블)
        hashed = hash_password(command.password)
        user = await self._auth_repository.save_user(
            email=email,
            name=command.name,
            password_hash=hashed,
            agreed=command.agreed,
            role=role,
        )

        # 4. 세션 발급
        access_token, expires_at = generate_access_token(user.id, user.email, role)
        refresh_token = secrets.token_hex(32)

        session_dto = UserSessionDTO(
            user_id=user.id,
            email=user.email,
            name=user.name or "",
            role=role,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )

        await self._auth_repository.save_session(session_dto)
        return session_dto

    async def login(self, command: LoginCommand) -> UserSessionDTO:
        email = command.email.strip()
        user = await self._auth_repository.find_user_by_email(email)
        if not user:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        # 비밀번호 해시 조회 및 검증
        hashed_password = await self._auth_repository.get_hashed_password(email)
        if not hashed_password or not verify_password(command.password, hashed_password):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        # 세션 발급 (역할은 로그인 시점의 화이트리스트 승격 여부로 결정)
        role = await self._resolve_role(email)
        access_token, expires_at = generate_access_token(user.id, user.email, role)
        refresh_token = secrets.token_hex(32)

        session_dto = UserSessionDTO(
            user_id=user.id,
            email=user.email,
            name=user.name or "",
            role=role,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )

        await self._auth_repository.save_session(session_dto)
        await self._auth_repository.update_last_login(user.id)
        return session_dto

    async def refresh_token(self, refresh_token: str) -> UserSessionDTO:
        # 리프레시 토큰으로 세션 조회
        session = await self._auth_repository.find_session_by_refresh_token(refresh_token)
        if not session:
            raise ValueError("유효하지 않거나 만료된 세션입니다.")

        # 만료 시간 검증
        if session.expires_at < datetime.utcnow():
            raise ValueError("세션이 만료되었습니다. 다시 로그인해주세요.")

        # 기존 토큰 무효화 (액세스 토큰 기준 세션 삭제)
        await self._auth_repository.delete_session_by_access_token(session.access_token)

        # 새 세션 발급 (승격/강등이 다음 갱신에 반영되도록 역할 재결정)
        role = await self._resolve_role(session.email)
        access_token, expires_at = generate_access_token(session.user_id, session.email, role)
        new_refresh_token = secrets.token_hex(32)

        new_session = UserSessionDTO(
            user_id=session.user_id,
            email=session.email,
            name=session.name,
            role=role,
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_at=expires_at
        )

        await self._auth_repository.save_session(new_session)
        return new_session

    async def logout(self, access_token: str) -> None:
        await self._auth_repository.delete_session_by_access_token(access_token)
