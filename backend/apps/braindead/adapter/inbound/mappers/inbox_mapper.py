from braindead.adapter.inbound.api.schemas.inbox_schema import InboxEmailResponse, ReceiveEmailRequest
from braindead.app.dtos.inbox_dto import InboxEmailDTO, ReceiveEmailCommand


class InboxMapper:
    @staticmethod
    def to_command(req: ReceiveEmailRequest) -> ReceiveEmailCommand:
        return ReceiveEmailCommand(
            gmail_message_id=req.gmail_message_id,
            from_email=req.from_email,
            from_name=req.from_name,
            subject=req.subject,
            body=req.body,
            received_at=req.received_at,
        )

    @staticmethod
    def to_response(dto: InboxEmailDTO) -> InboxEmailResponse:
        return InboxEmailResponse(
            id=dto.id or 0,
            gmail_message_id=dto.gmail_message_id,
            from_email=dto.from_email,
            from_name=dto.from_name,
            subject=dto.subject,
            body=dto.body,
            received_at=dto.received_at,
        )
