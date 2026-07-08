from fastapi import APIRouter, Depends, HTTPException, status
from mfds_admin.app.ports.input.admin_auth_use_case import AdminAuthUseCase
from mfds_admin.dependencies.admin_auth import get_admin_auth_use_case
from mfds_admin.adapter.inbound.api.schemas.admin_auth_schema import (
    AdminLoginRequestSchema,
    AdminTokenResponseSchema
)
from mfds_admin.app.dtos.admin_auth_dto import AdminLoginCommand

router = APIRouter(tags=["admin"])

@router.post("/admin/login", response_model=AdminTokenResponseSchema)
async def admin_login(
    req: AdminLoginRequestSchema,
    use_case: AdminAuthUseCase = Depends(get_admin_auth_use_case)
) -> AdminTokenResponseSchema:
    try:
        command = AdminLoginCommand(email=req.email, password=req.password)
        res = await use_case.login(command)
        return AdminTokenResponseSchema(
            access_token=res.access_token,
            token_type=res.token_type,
            expires_in=res.expires_in,
            admin_name=res.admin_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/admin/loginn", response_model=AdminTokenResponseSchema, include_in_schema=False)
async def admin_login_typo_alias(
    req: AdminLoginRequestSchema,
    use_case: AdminAuthUseCase = Depends(get_admin_auth_use_case)
) -> AdminTokenResponseSchema:
    return await admin_login(req, use_case)
