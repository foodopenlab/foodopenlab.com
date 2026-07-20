from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_admin.adapter.outbound.orm.expert_whitelist_orm import ExpertWhitelistORM
from mfds_admin.app.dtos.member_dto import MemberDTO
from mfds_admin.app.ports.output.member_repository import MemberRepositoryPort
from mfds_user.adapter.outbound.orm.expert_user_orm import ExpertUserORM


class MemberPgRepository(MemberRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_with_promotion(self) -> list[MemberDTO]:
        stmt = (
            select(ExpertUserORM, ExpertWhitelistORM.email)
            .outerjoin(ExpertWhitelistORM, ExpertWhitelistORM.email == ExpertUserORM.email)
            .order_by(ExpertUserORM.created_at.desc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            MemberDTO(
                id=str(user.id),
                email=user.email,
                name=user.name,
                auth_provider=user.auth_provider,
                is_expert=whitelist_email is not None,
                last_login=user.last_login,
                created_at=user.created_at,
            )
            for user, whitelist_email in rows
        ]
