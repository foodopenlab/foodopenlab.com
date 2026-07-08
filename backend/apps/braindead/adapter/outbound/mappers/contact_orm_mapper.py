from braindead.adapter.outbound.orm.contact_orm import ContactORM
from braindead.app.dtos.contact_dto import ContactDTO
from braindead.domain.entities.contact_entity import ContactEntity


class ContactOrmMapper:
    @staticmethod
    def to_orm(entity: ContactEntity) -> ContactORM:
        return ContactORM(
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            company=entity.company,
            note=entity.note,
        )

    @staticmethod
    def to_dto(orm: ContactORM) -> ContactDTO:
        return ContactDTO(
            id=orm.id,
            name=orm.name,
            email=orm.email,
            phone=orm.phone,
            company=orm.company,
            note=orm.note,
        )
