from typing import Callable

from ontology.classification.message_category import MessageCategory

from braindead.app.dtos.spam_dto import SpamCheckCommand, SpamResultDTO
from braindead.app.ports.input.spam_use_case import ISpamUseCase
from braindead.app.ports.output.llm_port import ILLMPort
from braindead.app.ports.output.spam_port import ISpamPort
from braindead.domain.entities.spam_entity import SpamEntity

_CLASSIFY_TEMPLATE = """다음 메시지를 분류하고 아래 형식으로만 답하세요.

형식:
판정: spam|legit|phishing|ad
이유: (한 줄 설명)

메시지:
{message}"""

_CATEGORY_MAP = {
    "spam": MessageCategory.SPAM,
    "legit": MessageCategory.LEGIT,
    "phishing": MessageCategory.PHISHING,
    "ad": MessageCategory.AD,
}

# Interpreter pattern: 각 행 접두사를 처리하는 핸들러 테이블
_LINE_HANDLERS: dict[str, Callable[[str, dict], None]] = {
    "판정:": lambda val, s: s.update({"category": _CATEGORY_MAP.get(val.lower(), MessageCategory.LEGIT)}),
    "이유:": lambda val, s: s.update({"reason": val}),
}


def _parse(raw: str) -> tuple[MessageCategory, str]:
    state: dict = {"category": MessageCategory.LEGIT, "reason": raw.strip()}
    for line in (l.strip() for l in raw.strip().splitlines() if l.strip()):
        lower = line.lower()
        for prefix, handler in _LINE_HANDLERS.items():
            if lower.startswith(prefix):
                handler(line[len(prefix):].strip(), state)
                break
    return state["category"], state["reason"]


class SpamInteractor(ISpamUseCase):
    def __init__(self, llm_port: ILLMPort, spam_port: ISpamPort) -> None:
        self._llm = llm_port
        self._spam = spam_port

    async def check(self, cmd: SpamCheckCommand) -> SpamResultDTO:
        raw = await self._llm.chat(_CLASSIFY_TEMPLATE.format(message=cmd.message))
        category, reason = _parse(raw)
        entity = SpamEntity(id=None, message=cmd.message, category=category, reason=reason)
        return await self._spam.save(entity)

    async def history(self) -> list[SpamResultDTO]:
        return await self._spam.find_all()
