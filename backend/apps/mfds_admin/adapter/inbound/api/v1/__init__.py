from fastapi import APIRouter
from mfds_admin.adapter.inbound.api.v1.admin_auth_router import router as admin_auth_router
from mfds_admin.adapter.inbound.api.v1.member_router import router as member_router
from mfds_admin.adapter.inbound.api.v1.admin_dashboard_router import router as admin_dashboard_router

admin_router = APIRouter()
admin_router.include_router(admin_auth_router)
admin_router.include_router(member_router)
admin_router.include_router(admin_dashboard_router)
