import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers.auto_channel_reply import channel
from app.handlers.moderation.ban import ban_router
from app.handlers.moderation.unban import unban_router
from app.handlers.moderation.mute import mute_router
from app.handlers.moderation.kick import kick_router
from config_reader import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.TOKEN.get_secret_value())
dp = Dispatcher()


async def main():
    dp.include_routers(ban_router, mute_router, kick_router, unban_router, channel)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен и начал опрос")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
