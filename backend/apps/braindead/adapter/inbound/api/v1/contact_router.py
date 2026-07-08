import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, UploadFile

from braindead.adapter.inbound.api.schemas.contact_schema import ContactResponse, UploadResultResponse
from braindead.adapter.inbound.mappers.contact_mapper import ContactMapper
from braindead.app.ports.input.contact_use_case import IContactUseCase
from braindead.dependencies.contact_provider import get_contact_use_case
from matrix.grid_admin_guard_manager import verify_admin_jwt

router = APIRouter(tags=["braindead"], dependencies=[Depends(verify_admin_jwt)])


@router.post("/braindead/contacts/upload", response_model=UploadResultResponse)
async def upload_contacts(
    file: UploadFile = File(...),
    use_case: IContactUseCase = Depends(get_contact_use_case),
) -> UploadResultResponse:
    text = (await file.read()).decode("utf-8", errors="replace").lstrip("﻿")
    rows = list(csv.DictReader(StringIO(text)))
    cmd = ContactMapper.csv_rows_to_command(rows)
    result = await use_case.upload(cmd)
    return UploadResultResponse(count=result.count)


@router.get("/braindead/contacts/search", response_model=list[ContactResponse])
async def search_contacts(
    q: str = "",
    use_case: IContactUseCase = Depends(get_contact_use_case),
) -> list[ContactResponse]:
    if not q.strip():
        return []
    dtos = await use_case.search(q.strip())
    return [ContactMapper.dto_to_response(dto) for dto in dtos]


@router.get("/braindead/contacts", response_model=list[ContactResponse])
async def list_contacts(
    use_case: IContactUseCase = Depends(get_contact_use_case),
) -> list[ContactResponse]:
    dtos = await use_case.list_all()
    return [ContactMapper.dto_to_response(dto) for dto in dtos]
