from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GatewayAuditLog:
    """
    시맨틱 게이트웨이를 통과한 모든 요청의 감사 로그(1행 = 1요청).

    분류 결과·차단 여부·응답 요약을 남겨 pgAdmin 모니터링과
    블랙유저 식별의 근거 데이터로 쓴다.
    """

    question: str
    destination: str  # search | rag | general | reject | error
    entities: list[str] = field(default_factory=list)
    blocked: bool = False
    answer_preview: str | None = None
    client_ip: str | None = None
    latency_ms: int | None = None
    id: int | None = None
    created_at: datetime | None = None
