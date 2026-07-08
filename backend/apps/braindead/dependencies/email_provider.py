from braindead.adapter.outbound.repositories.email_gateway import EmailGateway
from braindead.adapter.outbound.repositories.llm_gateway import BraindeadLLMGateway
from braindead.app.ports.input.email_use_case import IEmailUseCase
from braindead.app.use_cases.email_interactor import EmailInteractor

_PROMPT = "당신은 이메일 작성 전문가입니다. 사용자의 요청을 바탕으로 한국어로 전문적이고 정중한 이메일 본문을 작성해주세요."


def get_email_use_case() -> IEmailUseCase:
    return EmailInteractor(
        email_port=EmailGateway(),
        llm_port=BraindeadLLMGateway(system_prompt=_PROMPT),
    )
