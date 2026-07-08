from fastapi import Depends

from braindead.adapter.outbound.repositories.judge_repository import JudgeRepository
from braindead.app.ports.input.judge_use_case import IJudgeUseCase
from braindead.app.ports.output.judge_port import IJudgePort
from braindead.app.use_cases.judge_interactor import JudgeInteractor


def get_judge_port() -> IJudgePort:
    return JudgeRepository()


def get_judge_use_case(
    port: IJudgePort = Depends(get_judge_port),
) -> IJudgeUseCase:
    return JudgeInteractor(port=port)
