"""Composition Root — Port에 Adapter 주입 (DIP)."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from matrix.grid_redis_manager import get_redis

from auth.adapter.outbound.oauth.oauth_provider_factory import get_oauth_provider
from auth.adapter.outbound.pg.auth_identity_repository import AuthIdentityRepository
from auth.adapter.outbound.session.redis_oauth_state import RedisOAuthState
from auth.adapter.outbound.session.redis_refresh_session import RedisRefreshSession
from auth.adapter.outbound.token.rs256_token_issuer import Rs256TokenIssuer
from auth.app.ports.input.auth_use_case import IAuthUseCase
from auth.app.ports.output.identity_port import IIdentityPort
from auth.app.ports.output.oauth_state_port import IOAuthStatePort
from auth.app.ports.output.refresh_session_port import IRefreshSessionPort
from auth.app.ports.output.token_issuer_port import ITokenIssuerPort
from auth.app.use_cases.auth_interactor import AuthInteractor


def get_state_store() -> IOAuthStatePort:
    return RedisOAuthState(get_redis())


def get_refresh_session() -> IRefreshSessionPort:
    return RedisRefreshSession(get_redis())


def get_token_issuer() -> ITokenIssuerPort:
    return Rs256TokenIssuer()


def get_identity_repo(db: AsyncSession = Depends(get_db)) -> IIdentityPort:
    return AuthIdentityRepository(db)


def get_auth_use_case(
    identity: IIdentityPort = Depends(get_identity_repo),
    token_issuer: ITokenIssuerPort = Depends(get_token_issuer),
    refresh_session: IRefreshSessionPort = Depends(get_refresh_session),
    state_store: IOAuthStatePort = Depends(get_state_store),
) -> IAuthUseCase:
    return AuthInteractor(
        provider_factory=get_oauth_provider,
        identity=identity,
        token_issuer=token_issuer,
        refresh_session=refresh_session,
        state_store=state_store,
    )
