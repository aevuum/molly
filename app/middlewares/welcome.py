from collections.abc import Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from app.services.welcome import WelcomeService


class WelcomeMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable,
        event: Any,
        data: dict[str, Any],
    ) -> Any:

        if not isinstance(event, Message):
            return await handler(event, data)

        if event.chat.type not in {"group", "supergroup"}:
            return await handler(event, data)

        if event.chat.id != WelcomeService.VERIFICATION_CHAT_ID:
            return await handler(event, data)

        if not event.from_user or event.from_user.is_bot:
            return await handler(event, data)

        bot: Bot = data["bot"]

        verification = await WelcomeService.get_verification(
            chat_id=event.chat.id,
            user_id=event.from_user.id,
        )

        if verification is None:
            try:
                await event.delete()
            except TelegramBadRequest:
                pass

            await WelcomeService.register_user(
                chat_id=event.chat.id,
                user_id=event.from_user.id,
            )

            await WelcomeService.create_verification(
                bot=bot,
                chat_id=event.chat.id,
                user_id=event.from_user.id,
                first_name=event.from_user.first_name,
            )

            return

        if verification.verified:
            return await handler(event, data)

        try:
            await event.delete()
        except TelegramBadRequest:
            pass

        if verification.message_id is None:
            await WelcomeService.create_verification(
                bot=bot,
                chat_id=event.chat.id,
                user_id=event.from_user.id,
                first_name=event.from_user.first_name,
            )

        return