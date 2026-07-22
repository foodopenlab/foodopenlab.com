from abc import ABC, abstractmethod

from ontology.domain.entities.semantic_audit_log_entity import SemanticAuditLog


class IAuditLogPort(ABC):
    """Driven Port — 게이트웨이 감사 로그를 영속화한다."""

    @abstractmethod
    async def record(self, log: SemanticAuditLog) -> None: ...
