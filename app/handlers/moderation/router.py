from aiogram import Router

from app.handlers.moderation.ban import ban_router
from app.handlers.moderation.unban import unban_router
from app.handlers.moderation.mute import mute_router
from app.handlers.moderation.kick import kick_router
from app.handlers.moderation.warn import warn_router
from app.handlers.moderation.unwarn import unwarn_router
from app.middlewares.admin import AdminMiddleware


moderation_router = Router()

moderation_router.message.middleware(
    AdminMiddleware()
)

moderation_router.include_router(ban_router)
moderation_router.include_router(unban_router)
moderation_router.include_router(mute_router)
moderation_router.include_router(kick_router)
moderation_router.include_router(warn_router)
moderation_router.include_router(unwarn_router)