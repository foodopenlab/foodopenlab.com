from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.oauth.oauth_provider_factory import get_oauth_provider
from mfds_user.adapter.outbound.pg.oauth_user_pg_repository import OAuthUserPgRepository
from mfds_user.adapter.outbound.redis.redis_session_store_adapter import RedisSessionStoreAdapter
from mfds_user.app.ports.input.oauth_use_case import OAuthUseCase
from mfds_user.app.ports.output.oauth_user_repository import OAuthUserRepository
from mfds_user.app.ports.output.session_store_port import SessionStorePort
from mfds_user.app.use_cases.oauth_interactor import OAuthInteractor


def get_oauth_user_repository(db: AsyncSession = Depends(get_db)) -> OAuthUserRepository:
    return OAuthUserPgRepository(session=db)


def get_session_store() -> SessionStorePort:
    return RedisSessionStoreAdapter()


def get_oauth_use_case(
    user_repository: OAuthUserRepository = Depends(get_oauth_user_repository),
    session_store: SessionStorePort = Depends(get_session_store),
) -> OAuthUseCase:
    return OAuthInteractor(
        provider_factory=get_oauth_provider,
        user_repository=user_repository,
        session_store=session_store,
    )
