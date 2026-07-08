from dataclasses import dataclass, field


@dataclass
class ContactInputRow:
    name: str | None
    email: str | None
    phone: str | None
    company: str | None
    note: str | None


@dataclass
class ContactDTO:
    id: int | None
    name: str | None
    email: str | None
    phone: str | None
    company: str | None
    note: str | None


@dataclass
class UploadContactsCommand:
    rows: list[ContactInputRow] = field(default_factory=list)


@dataclass
class UploadResultDTO:
    count: int
