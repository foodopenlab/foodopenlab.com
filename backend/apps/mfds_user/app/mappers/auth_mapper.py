from __future__ import annotations
from typing import TYPE_CHECKING
from mfds_user.app.dtos.auth_dto import SignupCommand, LoginCommand

if TYPE_CHECKING:
    from mfds_user.adapter.inbound.api.schemas.auth_schema import SignupRequest, LoginRequest

def to_signup_command(req: SignupRequest) -> SignupCommand:
    return SignupCommand(
        email=req.email,
        password=req.password,
        name=req.name,
        agreed=req.agreed,
        role=req.role,
    )

def to_login_command(req: LoginRequest) -> LoginCommand:
    return LoginCommand(
        email=req.email,
        password=req.password,
    )
