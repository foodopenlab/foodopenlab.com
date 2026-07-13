from fastapi import APIRouter

from ontology.adapter.inbound.api.v1.vision_router import router as vision_myself_router

vision_router = APIRouter()
vision_router.include_router(vision_myself_router)
