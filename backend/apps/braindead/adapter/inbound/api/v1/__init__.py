from fastapi import APIRouter

from braindead.adapter.inbound.api.v1.contact_router import router as contact_router
from braindead.adapter.inbound.api.v1.discord_router import router as discord_router
from braindead.adapter.inbound.api.v1.email_router import router as email_router
from braindead.adapter.inbound.api.v1.inbox_router import router as inbox_router
from braindead.adapter.inbound.api.v1.spam_router import router as spam_router
from braindead.adapter.inbound.api.v1.judge_router import router as judge_router
from braindead.adapter.inbound.api.v1.telegram_router import router as telegram_router
from braindead.adapter.inbound.api.v1.watcher_router import router as watcher_router

braindead_router = APIRouter()
braindead_router.include_router(email_router)
braindead_router.include_router(inbox_router)
braindead_router.include_router(contact_router)
braindead_router.include_router(spam_router)
braindead_router.include_router(telegram_router)
braindead_router.include_router(discord_router)
braindead_router.include_router(watcher_router)
braindead_router.include_router(judge_router)
