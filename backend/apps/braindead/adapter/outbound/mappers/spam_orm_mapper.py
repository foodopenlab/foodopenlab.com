from ontology.classification.message_category import MessageCategory

from braindead.adapter.outbound.orm.spam_orm import SpamLogORM
from braindead.app.dtos.spam_dto import SpamResultDTO
from braindead.domain.entities.spam_entity import SpamEntity


class SpamOrmMapper:
    @staticmethod
    def to_orm(entity: SpamEntity) -> SpamLogORM:
        return SpamLogORM(
            message=entity.message,
            category=entity.category.value,
            reason=entity.reason,
        )

    @staticmethod
    def to_dto(orm: SpamLogORM) -> SpamResultDTO:
        return SpamResultDTO(
            id=orm.id,
            category=MessageCategory(orm.category),
            reason=orm.reason,
        )
