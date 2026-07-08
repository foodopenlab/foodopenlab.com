import json
import logging
import os
from typing import Any

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from mfds_user.app.ports.output.law_mcp_port import LawMcpPort, LawSearchResult

logger = logging.getLogger(__name__)


class KoreanLawMcpAdapter(LawMcpPort):
    def __init__(self) -> None:
        self._url = os.getenv("KOREAN_LAW_MCP_URL", "http://korean_law_mcp:3100/mcp")

    async def _call_tool(self, tool: str, args: dict[str, Any]) -> tuple[str, bool]:
        """반환: (텍스트, is_error). MCP 툴이 결과를 못 찾으면 isError=True로 명시적으로 알려준다."""
        async with streamablehttp_client(self._url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments=args)
                text = " ".join(
                    c.text for c in result.content if hasattr(c, "text")
                )
                return text, bool(result.isError)

    async def search_laws(self, query: str) -> list[LawSearchResult]:
        try:
            raw, is_error = await self._call_tool("search_law", {"query": query})
            if is_error:
                return []
            return _parse_law_results(raw)
        except Exception as e:
            logger.warning("korean-law-mcp search_law failed: %s", e)
            return []

    async def research_law(self, query: str, task: str = "full_research") -> str | None:
        """법령을 못 찾으면 None을 반환한다 — 호출부가 LLM에 못 찾은 상태를 억지로 채우게 하지 않도록."""
        try:
            raw, is_error = await self._call_tool(
                "legal_research",
                {"task": task, "query": query},
            )
            return None if is_error else raw
        except Exception as e:
            logger.warning("korean-law-mcp legal_research failed: %s", e)
            return None


def _parse_law_results(raw: str) -> list[LawSearchResult]:
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [
                LawSearchResult(
                    law_name=item.get("name") or item.get("법령명", ""),
                    law_id=item.get("id") or item.get("법령ID", ""),
                    url=item.get("url", ""),
                )
                for item in data
                if item.get("name") or item.get("법령명")
            ]
        if isinstance(data, dict) and "laws" in data:
            return _parse_law_results(json.dumps(data["laws"]))
    except (json.JSONDecodeError, TypeError):
        pass
    # plain-text fallback: 한 줄 = 법령명
    lines = [ln.strip().lstrip("-•·* ") for ln in raw.splitlines() if ln.strip()]
    return [LawSearchResult(law_name=ln, law_id="", url="") for ln in lines[:10]]
