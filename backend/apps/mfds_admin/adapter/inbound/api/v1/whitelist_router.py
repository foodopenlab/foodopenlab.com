from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import Annotated, List
from uuid import UUID
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.dependencies.whitelist import get_whitelist_use_case
from mfds_admin.adapter.inbound.api.middlewares.admin_auth_middleware import verify_admin_token
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import AdminTokenPayloadSchema
from mfds_admin.adapter.inbound.api.schemas.whitelist_schema import (
    AddWhitelistRequest,
    WhitelistResponse
)
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand

router = APIRouter(prefix="/admin/whitelist", tags=["admin"])

@router.post("", response_model=WhitelistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_whitelist(
    req: AddWhitelistRequest,
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: WhitelistUseCase = Depends(get_whitelist_use_case)
) -> WhitelistResponse:
    try:
        admin_id = UUID(admin.sub)
        command = AddWhitelistCommand(
            email=req.email,
            invited_name=req.invited_name,
            role_desc=req.role_desc,
            added_by=admin_id
        )
        res = await use_case.add_to_whitelist(command)
        return WhitelistResponse(
            email=res.email,
            invited_name=res.invited_name,
            role_desc=res.role_desc,
            added_by=str(res.added_by),
            added_at=res.added_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[WhitelistResponse])
async def list_whitelist(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: WhitelistUseCase = Depends(get_whitelist_use_case)
) -> List[WhitelistResponse]:
    res_list = await use_case.list_whitelist()
    return [
        WhitelistResponse(
            email=item.email,
            invited_name=item.invited_name,
            role_desc=item.role_desc,
            added_by=str(item.added_by),
            added_at=item.added_at
        )
        for item in res_list
    ]

@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_whitelist(
    email: str,
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: WhitelistUseCase = Depends(get_whitelist_use_case),
) -> Response:
    try:
        await use_case.remove_from_whitelist(email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
