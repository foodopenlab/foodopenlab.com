from __future__ import annotations

import json
import logging
import re

from ontology.app.dtos.scout_dto import ScoutPlan
from ontology.app.ports.output.command_interpreter_port import ICommandInterpreterPort
from ontology.app.ports.output.gemini_port import IGeminiPort

logger = logging.getLogger(__name__)

_PROMPT = (
    "당신은 웹 수집 명령 해석기입니다. 사용자의 자연어 명령을 읽고 아래 스키마의 JSON만 출력하세요. "
    "설명·마크다운·코드펜스 없이 순수 JSON 객체 하나만 출력합니다.\n\n"
    "실행 모드: {mode}  "
    "(crawler=시드 URL에서 링크를 따라가며 페이지 수집, scraper=대상 URL 본문 스크랩)\n\n"
    "필드:\n"
    "- max_pages: 정수 1~500. 크롤러가 방문할 최대 페이지 수. 명시 없으면 20.\n"
    "- max_depth: 정수 0~5. 시드로부터 탐색 깊이. 명시 없으면 2.\n"
    "- max_items: 정수 1~1000. 스크래퍼가 처리할 최대 URL 수. 명시 없으면 50.\n"
    "- keywords: 문자열 배열. 명령에 특정 주제·단어가 있으면 뽑고, 없으면 빈 배열 [].\n"
    "- reason: 한국어 한 문장. 명령을 어떻게 이해했는지 요약.\n\n"
    '명령: "{command}"\n\n'
    "JSON:"
)


class GeminiCommandInterpreterAdapter(ICommandInterpreterPort):
    """게이트웨이와 동일한 Gemini(IGeminiPort)로 자연어 명령을 실행 계획으로 해석한다.

    LLM 응답에서 JSON을 뽑아 파라미터로 정규화·클램핑하는 안티커럽션 경계.
    파싱 실패 시 예외 대신 안전한 기본값 계획을 돌려준다.
    """

    def __init__(self, gemini: IGeminiPort) -> None:
        self._gemini = gemini

    async def interpret(self, mode: str, command: str) -> ScoutPlan:
        if not command.strip():
            return ScoutPlan(reason="명령이 비어 있어 기본값으로 실행합니다.")

        text = await self._gemini.generate(_PROMPT.format(mode=mode, command=command.strip()))
        data = _parse_json(text)
        return ScoutPlan(
            max_pages=_clamp(data.get("max_pages"), 1, 500, 20),
            max_depth=_clamp(data.get("max_depth"), 0, 5, 2),
            max_items=_clamp(data.get("max_items"), 1, 1000, 50),
            keywords=_clean_keywords(data.get("keywords")),
            reason=str(data.get("reason") or "").strip()[:300],
        )


def _parse_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        logger.warning("[CommandInterpreter] JSON 미검출, 기본값 사용: %s", text[:120])
        return {}
    try:
        parsed = json.loads(match.group(0))
    except (json.JSONDecodeError, ValueError):
        logger.warning("[CommandInterpreter] JSON 디코드 실패, 기본값 사용")
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _clamp(value: object, lo: int, hi: int, default: int) -> int:
    try:
        n = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


def _clean_keywords(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned = [str(k).strip() for k in value if str(k).strip()]
    return cleaned[:20]
