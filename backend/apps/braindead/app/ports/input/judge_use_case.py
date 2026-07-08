from abc import ABC, abstractmethod

from braindead.adapter.inbound.api.schemas.judge_schema import JudgeSchema
from braindead.app.dtos.judge_dto import JudgeResponse


class IJudgeUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: JudgeSchema) -> JudgeResponse: ...
