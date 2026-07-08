import logging

from braindead.app.dtos.judge_dto import JudgeQuery, JudgeResponse
from braindead.app.ports.output.judge_port import IJudgePort

logger = logging.getLogger(__name__)


class JudgeRepository(IJudgePort):
    async def introduce_myself(self, query: JudgeQuery) -> JudgeResponse:
        logger.info("[JudgeRepository] introduce_myself | request=%s", query)
        return JudgeResponse(id=query.id, name=query.name)
