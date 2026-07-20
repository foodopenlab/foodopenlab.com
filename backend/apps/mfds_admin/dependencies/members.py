from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_admin.adapter.outbound.pg.member_pg_repository import MemberPgRepository
from mfds_admin.app.ports.input.member_use_case import MemberUseCase
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.app.ports.output.member_repository import MemberRepositoryPort
from mfds_admin.app.use_cases.member_interactor import MemberInteractor
from mfds_admin.dependencies.whitelist import get_whitelist_use_case


def get_member_repository(
    db: AsyncSession = Depends(get_db),
) -> MemberRepositoryPort:
    return MemberPgRepository(session=db)


def get_member_use_case(
    member_repository: MemberRepositoryPort = Depends(get_member_repository),
    whitelist_use_case: WhitelistUseCase = Depends(get_whitelist_use_case),
) -> MemberUseCase:
    return MemberInteractor(
        member_repository=member_repository,
        whitelist_use_case=whitelist_use_case,
    )
