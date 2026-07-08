from braindead.app.dtos.contact_dto import ContactDTO, ContactInputRow, UploadContactsCommand, UploadResultDTO
from braindead.app.ports.input.contact_use_case import IContactUseCase
from braindead.app.ports.output.contact_port import IContactPort
from braindead.domain.entities.contact_entity import ContactEntity


class ContactInteractor(IContactUseCase):
    def __init__(self, port: IContactPort) -> None:
        self._port = port

    async def upload(self, cmd: UploadContactsCommand) -> UploadResultDTO:
        entities = [
            ContactEntity(id=None, name=dto.name, email=dto.email, phone=dto.phone, company=dto.company, note=dto.note)
            for dto in cmd.rows
        ]
        return await self._port.save_all(entities)

    async def list_all(self) -> list[ContactDTO]:
        return await self._port.find_all()

    async def search(self, query: str) -> list[ContactDTO]:
        return await self._port.search(query)
