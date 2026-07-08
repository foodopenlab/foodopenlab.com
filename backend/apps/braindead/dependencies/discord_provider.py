from braindead.adapter.outbound.repositories.discord_gateway import DiscordGateway
from braindead.adapter.outbound.repositories.llm_gateway import BraindeadLLMGateway
from braindead.app.ports.input.discord_use_case import IDiscordUseCase
from braindead.app.use_cases.discord_interactor import DiscordInteractor

_PROMPT = "당신은 디스코드 메시지 처리 전문가입니다. 사용자의 요청을 바탕으로 친근하고 명확한 한국어 메시지를 작성해주세요."


def get_discord_use_case() -> IDiscordUseCase:
    return DiscordInteractor(
        discord_port=DiscordGateway(),
        llm_port=BraindeadLLMGateway(system_prompt=_PROMPT),
    )
