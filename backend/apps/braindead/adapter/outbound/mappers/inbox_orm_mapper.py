from braindead.adapter.outbound.orm.inbox_orm import InboxEmailORM
from braindead.app.dtos.inbox_dto import InboxEmailDTO
from braindead.domain.entities.inbox_entity import InboxEmailEntity


class InboxOrmMapper:
    @staticmethod
    def to_orm(entity: InboxEmailEntity) -> InboxEmailORM:
        return InboxEmailORM(
            gmail_message_id=entity.gmail_message_id,
            from_email=entity.from_email,
            from_name=entity.from_name,
            subject=entity.subject,
            body=entity.body,
            received_at=entity.received_at,
            embedding=entity.embedding,
        )

    @staticmethod
    def to_dto(orm: InboxEmailORM) -> InboxEmailDTO:
        return InboxEmailDTO(
            id=orm.id,
            gmail_message_id=orm.gmail_message_id,
            from_email=orm.from_email,
            from_name=orm.from_name,
            subject=orm.subject,
            body=orm.body,
            received_at=orm.received_at,
            embedding=orm.embedding,
        )
