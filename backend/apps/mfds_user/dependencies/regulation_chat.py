from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db

from mfds_user.adapter.outbound.mcp.korean_law_mcp_adapter import KoreanLawMcpAdapter
from mfds_user.adapter.outbound.pg.law_chunk_pg_repository import LawChunkPgRepository
from mfds_user.app.ports.input.regulation_chat_use_case import RegulationChatUseCase
from mfds_user.app.use_cases.law_chunk_interactor import LawChunkInteractor
from mfds_user.app.use_cases.regulation_chat_interactor import RegulationChatInteractor


def get_regulation_chat_use_case(
    db: AsyncSession = Depends(get_db),
) -> RegulationChatUseCase:
    # 하이브리드: 일반 질문은 law_chunks pgvector RAG, "최근 개정" 등은 MCP 실시간(interactor 내 분기)
    law_search = LawChunkInteractor(repo=LawChunkPgRepository(db))
    return RegulationChatInteractor(law_mcp=KoreanLawMcpAdapter(), law_search=law_search)
