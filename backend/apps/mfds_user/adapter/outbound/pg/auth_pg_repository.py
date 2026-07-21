from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.domain.entities.user_entity import User
from mfds_user.domain.value_objects.user_role_vo import UserRole
from matrix.orm.expert_user_orm import ExpertUserORM

class AuthPgRepository(AuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_all_active(self) -> list[User]:
        query = select(ExpertUserORM)
        result = await self.session.execute(query)
        db_users = result.scalars().all()
        # 역할의 SSOT는 화이트리스트(관리자 승격)이며 토큰 발급 시점에 결정된다.
        # 이 배치 조회는 role을 소비하지 않으므로 기본값 general로 채운다.
        return [
            User(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name,
                picture=db_user.picture,
                role=UserRole.GENERAL,
                created_at=db_user.created_at,
                last_login=db_user.last_login
            )
            for db_user in db_users
        ]
