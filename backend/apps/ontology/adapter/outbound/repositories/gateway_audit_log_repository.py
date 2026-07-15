from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ontology.adapter.outbound.orm.gateway_audit_log_orm import GatewayAuditLogORM
from ontology.app.ports.output.audit_log_port import IAuditLogPort
from ontology.domain.entities.gateway_audit_log_entity import GatewayAuditLog


class GatewayAuditLogRepository(IAuditLogPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record(self, log: GatewayAuditLog) -> None:
        self.session.add(self._to_orm(log))
        await self.session.commit()

    @staticmethod
    def _to_orm(log: GatewayAuditLog) -> GatewayAuditLogORM:
        return GatewayAuditLogORM(
            client_ip=log.client_ip,
            question=log.question,
            destination=log.destination,
            entities=log.entities,
            blocked=log.blocked,
            answer_preview=log.answer_preview,
            latency_ms=log.latency_ms,
        )
