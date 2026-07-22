"""Inbound 경계 톨게이트 — dto ↔ schema 변환."""

from __future__ import annotations

from auth.adapter.inbound.api.schemas.auth_schema import TokenResponse
from auth.app.dtos.auth_dto import TokenBundle


def to_token_response(bundle: TokenBundle) -> TokenResponse:
    return TokenResponse(
        access_token=bundle.access_token,
        refresh_token=bundle.refresh_token,
        token_type=bundle.token_type,
        expires_in=bundle.expires_in,
        sub=bundle.sub,
        roles=bundle.roles,
    )
