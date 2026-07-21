from braindead.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from braindead.app.ports.input.judge_use_case import IJudgeUseCase
from braindead.app.ports.output.judge_port import IJudgePort


class JudgeInteractor(IJudgeUseCase):
    def __init__(self, port: IJudgePort) -> None:
        self._port = port

    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        return await self._port.introduce_myself(query)
