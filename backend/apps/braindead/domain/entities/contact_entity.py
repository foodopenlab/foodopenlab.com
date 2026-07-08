from dataclasses import dataclass


@dataclass
class ContactEntity:
    id: int | None
    name: str | None
    email: str | None
    phone: str | None
    company: str | None
    note: str | None
