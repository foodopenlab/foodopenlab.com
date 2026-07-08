import asyncio
import logging
import os
import secrets

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from mfds_user.app.dtos.regulation_chat_dto import (
    LawReference,
    RegulationChatQuery,
    RegulationChatResponse,
)
from mfds_user.app.ports.output.law_mcp_port import LawMcpPort, LawSearchResult

logger = logging.getLogger(__name__)

_NO_LAW_FOUND_REPLY = "확인이 필요합니다 — law.go.kr에서 직접 확인을 권장합니다."

_AMENDMENT_KW = ("최근", "개정", "바뀐", "달라진", "변경", "신설", "폐지", "2025", "2026")
_ACTION_BASIS_KW = ("처분", "과징금", "위반", "제재", "영업정지", "벌칙", "과태료", "행정처분")
_LAW_SYSTEM_KW = ("체계", "시행령", "시행규칙", "위임", "하위법령")
_PROCEDURE_KW = ("절차", "방법", "수수료", "신청", "허가", "등록", "요건")


def _pick_task(message: str) -> str | None:
    if any(kw in message for kw in _AMENDMENT_KW):
        return "amendment_track"
    if any(kw in message for kw in _ACTION_BASIS_KW):
        return "action_basis"
    if any(kw in message for kw in _LAW_SYSTEM_KW):
        return "law_system"
    if any(kw in message for kw in _PROCEDURE_KW):
        return "procedure_detail"
    return None


class RegulationChatInteractor:
    def __init__(self, law_mcp: LawMcpPort) -> None:
        self._law_mcp = law_mcp
        self._llm = ChatOllama(
            model=os.getenv("EXAONE_MODEL", "exaone3.5:2.4b"),
            base_url=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"),
            temperature=0.3,
        )

    async def chat(self, query: RegulationChatQuery) -> RegulationChatResponse:
        task = _pick_task(query.message)

        if task:
            law_context = await self._law_mcp.research_law(query.message, task)
            referenced_laws: list[LawSearchResult] = []
            if law_context is None:
                return RegulationChatResponse(
                    reply=_NO_LAW_FOUND_REPLY,
                    referenced_laws=[],
                    session_key=query.session_key or f"reg-{secrets.token_hex(6)}",
                )
        else:
            laws = await self._law_mcp.search_laws(query.message)
            if not laws:
                return RegulationChatResponse(
                    reply=_NO_LAW_FOUND_REPLY,
                    referenced_laws=[],
                    session_key=query.session_key or f"reg-{secrets.token_hex(6)}",
                )
            law_context = _format_law_context(laws)
            referenced_laws = laws

        messages: list = [SystemMessage(content=_system_prompt(query.company_type, law_context))]
        for h in query.history[-10:]:
            cls = HumanMessage if h.role == "user" else AIMessage
            messages.append(cls(content=h.content))
        messages.append(HumanMessage(content=query.message))

        response = await asyncio.to_thread(self._llm.invoke, messages)

        return RegulationChatResponse(
            reply=str(response.content),
            referenced_laws=[LawReference(law_name=l.law_name) for l in referenced_laws if l.law_name],
            session_key=query.session_key or f"reg-{secrets.token_hex(6)}",
        )


def _format_law_context(laws: list[LawSearchResult]) -> str:
    return "\n".join(
        f"- {l.law_name}" + (f"  {l.url}" if l.url else "")
        for l in laws
    )


_FEW_SHOT = """
[답변 예시 — 이 형식을 따르세요]

Q: 식품제조가공업에서 HACCP 의무 대상인가요?
A: [법령 조회 결과 기반]
   • 식품위생법 시행규칙 제62조에 따라 매출액 1억 원 이상 식품제조가공업체는
     HACCP 의무 적용 대상입니다.
   • 단계적 의무화: 매출액 규모에 따라 적용 시기가 다릅니다.
   출처: 식품위생법 시행규칙 제62조, 별표 18

Q: 식품 표시에서 영양성분 표시 의무가 있나요?
A: [법령 조회 결과 기반]
   • 식품 등의 표시·광고에 관한 법률 제4조에 따라 가공식품은 영양성분을
     표시해야 합니다.
   • 2026년부터 의무 대상 품목이 259개로 확대됩니다.
   출처: 식품 등의 표시·광고에 관한 법률 제4조
"""


def _system_prompt(company_type: str, law_context: str) -> str:
    return f"""당신은 한국 식품법규 전문 AI입니다.
사용자 회사 업종: {company_type}

[MCP를 통해 조회한 법령 정보]
{law_context}

[답변 규칙]
- 반드시 위 법령 조회 결과를 근거로만 답변하세요.
- 조회 결과에 없는 조문·수치를 절대 만들지 마세요.
- 법령명과 조문번호를 반드시 "출처:" 형태로 명시하세요.
- 정보가 부족하면 "확인이 필요합니다 — law.go.kr에서 직접 확인을 권장합니다"라고만 답하세요.
- {company_type} 업종에 해당하는 내용만 추려서 글머리 기호(•)로 요약하세요.
{_FEW_SHOT}"""
