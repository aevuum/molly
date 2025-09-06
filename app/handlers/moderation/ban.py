import re
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from typing import Any
from aiogram.exceptions import TelegramBadRequest
from app.func.parseTime import parse_time
from app.func.getUserByIdOrUsername import get_user_by_username_or_id
from contextlib import suppress

ban_router = Router()


@ban_router.message(Command("ban"), F.chat.type.in_({"supergroup", "group"}))
async def ban_func(message: Message, bot: Bot, command: CommandObject) -> Any:
    user_id = None
    mention = None

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user = message.reply_to_message.from_user
        mention = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
    elif command and command.args:
        args = command.args.strip().split()
        if not args:
            await message.answer("❌ Укажите @username или ID пользователя!")
            return

        target = args[0]  # Это будет "@panaceyya_dev" или "123456789"

        try:
            # Правильный вызов функции с тремя аргументами
            user_id, mention = await get_user_by_username_or_id(
                bot, message.chat.id, target
            )
        except ValueError as e:
            await message.answer(f"❌ {e}")
            return
        except Exception as e:
            await message.answer(f"❌ Произошла ошибка: {e}")
            return
    else:
        await message.answer(
            "❌ Ответьте на сообщение или укажите @username/ID пользователя!"
        )
        return

    # ... остальной код

    # Парсим время из аргументов
    time_args = (
        command.args.split(maxsplit=1)[1]
        if command.args and len(command.args.split()) > 1
        else ""
    )
    until_date = parse_time(time_args)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date,
        )

        if until_date:
            time_str = until_date.strftime("%d.%m.%Y %H:%M")
            await message.answer(
                f"💜🔪 Пользователь {mention} забанен до <b>{time_str}</b>.",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"💜🔪 Пользователь {mention} забанен навсегда.",
                parse_mode="HTML",
            )
