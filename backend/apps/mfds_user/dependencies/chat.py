from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.llm.ollama_adapter import OllamaAdapter
from mfds_user.adapter.outbound.pg.chat_pg_repository import ChatPgRepository
from mfds_user.app.ports.input.chat_use_case import ChatUseCase
from mfds_user.app.ports.output.anonymous_repository import AnonymousRepository
from mfds_user.app.ports.output.chat_repository import ChatRepository
from mfds_user.app.ports.output.llm_port import LlmPort
from mfds_user.app.use_cases.chat_interactor import ChatInteractor
from mfds_user.dependencies.anonymous import get_anonymous_repository


def get_chat_repository(
    db: AsyncSession = Depends(get_db),
) -> ChatRepository:
    return ChatPgRepository(session=db)


def get_llm_port() -> LlmPort:
    return OllamaAdapter()


def get_chat_use_case(
    chat_repository: ChatRepository = Depends(get_chat_repository),
    anonymous_repository: AnonymousRepository = Depends(get_anonymous_repository),
    llm_port: LlmPort = Depends(get_llm_port),
) -> ChatUseCase:
    return ChatInteractor(
        chat_repository=chat_repository,
        anonymous_repository=anonymous_repository,
        llm_port=llm_port,
    )
