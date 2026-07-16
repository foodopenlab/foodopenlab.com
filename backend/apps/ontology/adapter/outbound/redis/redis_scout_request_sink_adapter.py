from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict

from matrix.grid_redis_manager import get_redis
from ontology.adapter.outbound.redis import redis_keys
from ontology.app.dtos.scout_dto import ScoutPlan
from ontology.app.ports.output.scout_request_sink_port import IScoutRequestSinkPort

logger = logging.getLogger(__name__)

# 이력이 무한정 쌓이지 않도록 최근 N개만 유지한다.
_MAX_HISTORY = 500


class RedisScoutRequestSinkAdapter(IScoutRequestSinkPort):
    """스카우트 입력을 Redis LIST(ontology:scout:requests)에 JSON으로 RPUSH 한다."""

    async def record(self, mode: str, url: str, command: str, plan: ScoutPlan) -> None:
        entry = json.dumps(
            {
                "mode": mode,
                "url": url,
                "command": command,
                "plan": asdict(plan),
                "at": int(time.time()),
            },
            ensure_ascii=False,
        )
        redis = get_redis()
        await redis.rpush(redis_keys.SCOUT_REQUESTS, entry)
        await redis.ltrim(redis_keys.SCOUT_REQUESTS, -_MAX_HISTORY, -1)
        logger.info("[RedisScoutRequestSink] recorded mode=%s url=%s", mode, url)
