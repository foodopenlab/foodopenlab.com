from abc import ABC, abstractmethod

from braindead.app.dtos.judge_dto import JudgeQuery, JudgeResponse


class IJudgeUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse: ...
