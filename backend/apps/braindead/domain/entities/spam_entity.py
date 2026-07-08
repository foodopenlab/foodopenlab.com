from dataclasses import dataclass

from ontology.classification.message_category import MessageCategory


@dataclass
class SpamEntity:
    id: int | None
    message: str
    category: MessageCategory
    reason: str
