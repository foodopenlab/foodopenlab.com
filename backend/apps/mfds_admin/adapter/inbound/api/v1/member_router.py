from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from mfds_admin.adapter.inbound.api.middlewares.admin_auth_middleware import verify_admin_token
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import AdminTokenPayloadSchema
from mfds_admin.adapter.inbound.api.schemas.member_schema import MemberResponse
from mfds_admin.app.ports.input.member_use_case import MemberUseCase
from mfds_admin.dependencies.members import get_member_use_case

router = APIRouter(prefix="/admin/members", tags=["admin"])


@router.get("", response_model=List[MemberResponse])
async def list_members(
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> List[MemberResponse]:
    members = await use_case.list_members()
    return [
        MemberResponse(
            id=m.id,
            email=m.email,
            name=m.name,
            auth_provider=m.auth_provider,
            is_expert=m.is_expert,
            last_login=m.last_login,
            created_at=m.created_at,
        )
        for m in members
    ]


@router.post("/{email}/promote", status_code=status.HTTP_204_NO_CONTENT)
async def promote_member(
    email: str,
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> Response:
    await use_case.promote(email, UUID(admin.sub))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{email}/demote", status_code=status.HTTP_204_NO_CONTENT)
async def demote_member(
    email: str,
    admin: Annotated[AdminTokenPayloadSchema, Depends(verify_admin_token)],
    use_case: MemberUseCase = Depends(get_member_use_case),
) -> Response:
    await use_case.demote(email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
