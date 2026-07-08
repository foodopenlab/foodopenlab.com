from braindead.adapter.inbound.api.schemas.contact_schema import ContactResponse
from braindead.app.dtos.contact_dto import ContactDTO, ContactInputRow, UploadContactsCommand

# Google Contacts 내보내기 형식 컬럼 매핑
_GOOGLE_EMAIL_COLS = ["e-mail 1 - value", "e-mail 2 - value"]
_GOOGLE_PHONE_COLS = ["phone 1 - value", "phone 2 - value"]
_GOOGLE_COMPANY_COLS = ["organization name", "organization 1 - name"]


class ContactMapper:
    @staticmethod
    def csv_rows_to_command(raw_rows: list[dict]) -> UploadContactsCommand:
        dtos = [ContactMapper._to_dto(row) for row in raw_rows]
        return UploadContactsCommand(rows=[d for d in dtos if d is not None])

    @staticmethod
    def dto_to_response(dto: ContactDTO) -> ContactResponse:
        return ContactResponse(
            id=dto.id or 0,
            name=dto.name,
            email=dto.email,
            phone=dto.phone,
            company=dto.company,
            note=dto.note,
        )

    @staticmethod
    def _to_dto(row: dict) -> ContactInputRow | None:
        clean: dict[str, str] = {
            k.strip().lstrip("﻿").lower(): (v.strip() if v else "")
            for k, v in row.items()
            if k is not None
        }

        # ── 이름 ─────────────────────────────────────────────────────
        name: str | None = clean.get("name") or clean.get("이름") or None
        if name is None:
            first = clean.get("first name", "")
            last = clean.get("last name", "")
            name = f"{first} {last}".strip() or clean.get("nickname") or None

        # ── 이메일 ───────────────────────────────────────────────────
        email: str | None = next(
            (clean[c] for c in ["email", "이메일", "mail"] + _GOOGLE_EMAIL_COLS if clean.get(c)),
            None,
        )

        # 이름·이메일 모두 없으면 빈 행으로 간주
        if not name and not email:
            return None

        # ── 전화 ─────────────────────────────────────────────────────
        phone: str | None = next(
            (clean[c] for c in ["phone", "전화", "휴대폰", "전화번호"] + _GOOGLE_PHONE_COLS if clean.get(c)),
            None,
        )

        # ── 회사 ─────────────────────────────────────────────────────
        company: str | None = next(
            (clean[c] for c in ["company", "회사", "기관"] + _GOOGLE_COMPANY_COLS if clean.get(c)),
            None,
        )

        # ── 메모 ─────────────────────────────────────────────────────
        note: str | None = next(
            (clean[c] for c in ["note", "메모", "비고", "notes"] if clean.get(c)),
            None,
        )

        return ContactInputRow(name=name, email=email, phone=phone, company=company, note=note)
