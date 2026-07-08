from ontology.classification.message_category import MessageCategory

from braindead.adapter.inbound.api.schemas.spam_schema import SpamCheckResponse
from braindead.app.dtos.spam_dto import SpamCheckCommand, SpamResultDTO

_SPAM_CATEGORIES = {MessageCategory.SPAM, MessageCategory.PHISHING, MessageCategory.AD}


class SpamMapper:
    @staticmethod
    def to_command(message: str) -> SpamCheckCommand:
        return SpamCheckCommand(message=message)

    @staticmethod
    def to_response(dto: SpamResultDTO) -> SpamCheckResponse:
        return SpamCheckResponse(
            id=dto.id or 0,
            category=dto.category,
            reason=dto.reason,
            is_spam=dto.category in _SPAM_CATEGORIES,
        )
