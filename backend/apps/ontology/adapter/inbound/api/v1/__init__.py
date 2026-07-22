from fastapi import APIRouter

from ontology.adapter.inbound.api.v1.crawler_router import router as crawler_router
from ontology.adapter.inbound.api.v1.semantic_router import router as semantic_router
from ontology.adapter.inbound.api.v1.scout_router import router as scout_router
from ontology.adapter.inbound.api.v1.scraper_router import router as scraper_router
from ontology.adapter.inbound.api.v1.vision_router import router as vision_myself_router

vision_router = APIRouter()
vision_router.include_router(vision_myself_router)
vision_router.include_router(semantic_router)
vision_router.include_router(crawler_router)
vision_router.include_router(scraper_router)
vision_router.include_router(scout_router)
