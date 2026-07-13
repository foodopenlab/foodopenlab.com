from dataclasses import dataclass

from ontology.domain.value_objects.classification.message_category import MessageCategory


@dataclass
class SpamCheckCommand:
    message: str


@dataclass
class SpamResultDTO:
    id: int | None
    category: MessageCategory
    reason: str
