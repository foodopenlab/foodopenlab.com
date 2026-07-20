from fastapi import APIRouter
from mfds_user.adapter.inbound.api.v1.auth_router import router as auth_router
from mfds_user.adapter.inbound.api.v1.oauth_router import router as oauth_router
from mfds_user.adapter.inbound.api.v1.agent_router import router as agent_router
from mfds_user.adapter.inbound.api.v1.recall_router import router as recall_router
from mfds_user.adapter.inbound.api.v1.enforcement_router import router as enforcement_router
from mfds_user.adapter.inbound.api.v1.food_poisoning_stat_router import router as food_poisoning_stat_router
from mfds_user.adapter.inbound.api.v1.haccp_router import router as haccp_router
from mfds_user.adapter.inbound.api.v1.supplier_router import router as supplier_router
from mfds_user.adapter.inbound.api.v1.mypage_router import router as mypage_router
from mfds_user.adapter.inbound.api.v1.regulation_router import router as regulation_router
from mfds_user.adapter.inbound.api.v1.regulation_chat_router import router as regulation_chat_router
from mfds_user.adapter.inbound.api.v1.law_chunk_router import router as law_chunk_router
from mfds_user.adapter.inbound.api.v1.industry_router import router as industry_router
from mfds_user.adapter.inbound.api.v1.daily_report_router import router as daily_report_router
from mfds_user.adapter.inbound.api.v1.report_feedback_router import router as report_feedback_router
from mfds_user.adapter.inbound.api.v1.data_sync_router import router as data_sync_router

user_router = APIRouter()
user_router.include_router(auth_router)
user_router.include_router(oauth_router)
user_router.include_router(agent_router)
user_router.include_router(recall_router)
user_router.include_router(enforcement_router)
user_router.include_router(food_poisoning_stat_router)
user_router.include_router(data_sync_router)
user_router.include_router(haccp_router)
user_router.include_router(supplier_router)
user_router.include_router(mypage_router)
user_router.include_router(regulation_router)
user_router.include_router(regulation_chat_router)
user_router.include_router(law_chunk_router)
user_router.include_router(industry_router)
user_router.include_router(daily_report_router)
user_router.include_router(report_feedback_router)
