from braindead.adapter.outbound.repositories.llm_gateway import BraindeadLLMGateway
from braindead.adapter.outbound.repositories.telegram_gateway import TelegramGateway
from braindead.app.ports.input.telegram_use_case import ITelegramUseCase
from braindead.app.use_cases.telegram_interactor import TelegramInteractor

_PROMPT = "당신은 텔레그램 메시지 처리 전문가입니다. 사용자의 요청을 바탕으로 간결하고 명확한 한국어 메시지를 작성해주세요."


def get_telegram_use_case() -> ITelegramUseCase:
    return TelegramInteractor(
        telegram_port=TelegramGateway(),
        llm_port=BraindeadLLMGateway(system_prompt=_PROMPT),
    )
