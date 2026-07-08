from mfds_user.adapter.outbound.mcp.korean_law_mcp_adapter import KoreanLawMcpAdapter
from mfds_user.app.ports.input.regulation_chat_use_case import RegulationChatUseCase
from mfds_user.app.use_cases.regulation_chat_interactor import RegulationChatInteractor


def get_regulation_chat_use_case() -> RegulationChatUseCase:
    return RegulationChatInteractor(law_mcp=KoreanLawMcpAdapter())
