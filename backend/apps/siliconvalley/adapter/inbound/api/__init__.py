"""Silicon Valley inbound HTTP — v1 piper routers aggregated for FastAPI registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

    piper_router: APIRouter

__all__ = ["piper_router"]

_piper_router: APIRouter | None = None


def _build_piper_router() -> APIRouter:
    from fastapi import APIRouter

    from siliconvalley.adapter.inbound.api.v1.piper_bighetti_hr_router import bighetti_router
    from siliconvalley.adapter.inbound.api.v1.piper_dinesh_dash_router import dinesh_router
    from siliconvalley.adapter.inbound.api.v1.piper_dunn_coo_router import dunn_router
    from siliconvalley.adapter.inbound.api.v1.piper_gilfoyle_sys_router import gilfoyle_router
    from siliconvalley.adapter.inbound.api.v1.piper_hendricks_ceo_router import hendricks_router

    router = APIRouter(prefix="/piper", tags=["piper"])
    router.include_router(bighetti_router)
    router.include_router(dinesh_router)
    router.include_router(dunn_router)
    router.include_router(gilfoyle_router)
    router.include_router(hendricks_router)
    return router


def __getattr__(name: str):
    global _piper_router
    if name == "piper_router":
        if _piper_router is None:
            _piper_router = _build_piper_router()
        return _piper_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
