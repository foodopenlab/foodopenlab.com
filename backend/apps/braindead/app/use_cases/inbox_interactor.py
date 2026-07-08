from matrix.grid_embedding_manager import embed_text

from braindead.app.dtos.inbox_dto import InboxEmailDTO, ReceiveEmailCommand
from braindead.app.ports.input.inbox_use_case import IInboxUseCase
from braindead.app.ports.output.inbox_port import IInboxPort
from braindead.domain.entities.inbox_entity import InboxEmailEntity


class InboxInteractor(IInboxUseCase):
    def __init__(self, port: IInboxPort) -> None:
        self._port = port

    async def receive(self, cmd: ReceiveEmailCommand) -> InboxEmailDTO:
        embedding = await embed_text(f"{cmd.subject}\n\n{cmd.body}")
        entity = InboxEmailEntity(
            id=None,
            gmail_message_id=cmd.gmail_message_id,
            from_email=cmd.from_email,
            from_name=cmd.from_name,
            subject=cmd.subject,
            body=cmd.body,
            received_at=cmd.received_at,
            embedding=embedding,
        )
        return await self._port.save(entity)

    async def list_all(self) -> list[InboxEmailDTO]:
        return await self._port.find_all()
