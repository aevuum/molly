from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from typing import Any
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

unban_router = Router()


@unban_router.message(Command("unban"), F.chat.type.in_({"supergroup", "group"}))
async def unban_func(message: Message, bot: Bot, command: CommandObject) -> Any:
    user_id = None
    mention = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user = message.reply_to_message.from_user
        mention = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
    elif command and command.args:
        target = command.args.strip()

        if target.startswith("@"):
            username = target[1:]
            try:
                user = await bot.get_chat(f"@{username}")
                user_id = user.id
                user_name = user.first_name or user.username or username
                mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
            except TelegramBadRequest:
                await message.answer(f"❌ Пользователь @{username} не найден.")
                return
        else:
            try:
                user_id = int(target)
                try:
                    user = await bot.get_chat(user_id)
                    user_name = user.first_name or user.username or "пользователь"
                    mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
                except TelegramBadRequest:
                    mention = f"<a href='tg://user?id={user_id}'>пользователь</a>"
            except ValueError:
                await message.answer(
                    "❌ Неверный формат. Используйте @username или числовой ID."
                )
                return
    else:
        await message.answer(
            "❌ Ответьте на сообщение или укажите @username/ID пользователя!"
        )
        return

    with suppress(TelegramBadRequest):
        await bot.unban_chat_member(
            chat_id=message.chat.id, user_id=user_id, only_if_banned=True
        )

        await message.answer(
            f"💜✅ Пользователь {mention} разбанен.",
            parse_mode="HTML",
        )
