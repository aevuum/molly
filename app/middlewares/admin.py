from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


MODERATION_COMMANDS = {
    "ban",
    "unban",
    "mute",
    "unmute",
    "kick",
    "warn",
    "unwarn",
}


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        command_name = None
        if event.text and event.text.startswith("/"):
            command_name = event.text.split()[0][1:].split("@", 1)[0].lower()

        if command_name not in MODERATION_COMMANDS:
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        bot: Bot = data["bot"]

        moderator = await bot.get_chat_member(
            chat_id=event.chat.id,
            user_id=event.from_user.id,
        )

        if moderator.status not in {
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }:
            await event.answer("💜❌ У вас нет прав администратора.")
            return

        target_id = None

        if event.reply_to_message and event.reply_to_message.from_user:
            target_id = event.reply_to_message.from_user.id
        elif event.text:
            parts = event.text.split()

            if len(parts) > 1:
                target = parts[1]

                if target.isdigit():
                    target_id = int(target)
                elif target.startswith("@"):
                    try:
                        target_user = await bot.get_chat(target)
                        target_id = target_user.id
                    except TelegramBadRequest:
                        pass

        if target_id is not None:
            target = await bot.get_chat_member(
                chat_id=event.chat.id,
                user_id=target_id,
            )

            if target.status in {
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            }:
                await event.answer(
                    "💜❌ Невозможно применить команду на администраторе."
                )
                return

        result = await handler(event, data)

        if (
            command_name in MODERATION_COMMANDS
            and event.reply_to_message is not None
        ):
            try:
                await event.reply_to_message.delete()
            except TelegramBadRequest:
                pass

        return result
