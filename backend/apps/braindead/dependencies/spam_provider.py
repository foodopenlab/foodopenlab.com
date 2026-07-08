from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.repositories.llm_gateway import BraindeadLLMGateway
from braindead.adapter.outbound.repositories.spam_repository import SpamRepository
from braindead.app.ports.input.spam_use_case import ISpamUseCase
from braindead.app.use_cases.spam_interactor import SpamInteractor
from matrix.grid_oracle_database_manager import get_db

_PROMPT = "당신은 스팸 메시지 분류 전문가입니다. spam·legit·phishing·ad 중 하나로 판정하고 이유를 한국어로 설명해주세요."


def get_spam_use_case(db: AsyncSession = Depends(get_db)) -> ISpamUseCase:
    return SpamInteractor(
        llm_port=BraindeadLLMGateway(system_prompt=_PROMPT),
        spam_port=SpamRepository(session=db),
    )
