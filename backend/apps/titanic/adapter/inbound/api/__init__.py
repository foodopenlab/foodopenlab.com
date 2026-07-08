"""Titanic inbound HTTP — v1 character routers aggregated for FastAPI registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

    titanic_router: APIRouter

__all__ = ["titanic_router"]

_titanic_router: APIRouter | None = None


def _build_titanic_router() -> APIRouter:
    from fastapi import APIRouter

    from titanic.adapter.inbound.api.v1.crew_andrews_architect_router import (
        andrews_architect_router as crew_andrews_architect_router,
    )
    from titanic.adapter.inbound.api.v1.crew_hartley_violin_router import (
        hartley_violin_router as crew_hartley_violin_router,
    )
    from titanic.adapter.inbound.api.v1.crew_james_director_router import crew_james_director_router
    from titanic.adapter.inbound.api.v1.crew_lowe_boat_router import (
        lowe_boat_router as crew_lowe_boat_router,
    )
    from titanic.adapter.inbound.api.v1.crew_smith_captain_router import smith_captain_router
    from titanic.adapter.inbound.api.v1.crew_walter_roaster_router import (
        walter_roaster_router as crew_walter_roaster_router,
    )
    from titanic.adapter.inbound.api.v1.passenger_cal_tester_router import passenger_cal_tester_router
    from titanic.adapter.inbound.api.v1.passenger_isidor_couple_router import passenger_isidor_couple_router
    from titanic.adapter.inbound.api.v1.passenger_jack_trainer_router import passenger_jack_trainer_router
    from titanic.adapter.inbound.api.v1.passenger_molly_scaler_router import passenger_molly_scaler_router
    from titanic.adapter.inbound.api.v1.passenger_rose_model_router import passenger_rose_model_router
    from titanic.adapter.inbound.api.v1.passenger_ruth_validation_router import passenger_ruth_validation_router

    router = APIRouter(prefix="/titanic", tags=["titanic"])
    router.include_router(crew_andrews_architect_router)
    router.include_router(crew_hartley_violin_router)
    router.include_router(crew_james_director_router)
    router.include_router(crew_lowe_boat_router)
    router.include_router(smith_captain_router)
    router.include_router(crew_walter_roaster_router)
    router.include_router(passenger_cal_tester_router)
    router.include_router(passenger_isidor_couple_router)
    router.include_router(passenger_jack_trainer_router)
    router.include_router(passenger_molly_scaler_router)
    router.include_router(passenger_rose_model_router)
    router.include_router(passenger_ruth_validation_router)
    return router


def __getattr__(name: str):
    global _titanic_router
    if name == "titanic_router":
        if _titanic_router is None:
            _titanic_router = _build_titanic_router()
        return _titanic_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
