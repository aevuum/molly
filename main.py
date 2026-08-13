import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.database.database import close_database
from app.handlers.auto_channel_reply import channel
from app.handlers.moderation.router import moderation_router
from config_reader import config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=config.TOKEN.get_secret_value()
)

dp = Dispatcher()


async def main():
    dp.include_routers(
        moderation_router,
        channel,
    )

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    logger.info(
        "Бот запущен и начал опрос"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        close_database()