from contextlib import suppress
from typing import Any

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.func.getUserByIdOrUsername import get_user_by_username_or_id
from app.func.parseTime import parse_time
from app.func.time import format_datetime


ban_router = Router()


@ban_router.message(Command("ban"), F.chat.type.in_({"supergroup", "group"}))
async def ban_func(message: Message, bot: Bot, command: CommandObject) -> Any:
    user_id = None
    mention = None
    duration_string = None

    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        user = message.reply_to_message.from_user
        mention = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"

        args = command.args.strip().split() if command.args else []
        if args:
            duration_string = args[0]
    elif command.args:
        args = command.args.strip().split()
        target = args[0]

        try:
            user_id, mention = await get_user_by_username_or_id(
                bot, message.chat.id, target
            )
        except ValueError as e:
            await message.answer(f"❌ {e}")
            return
        except Exception as e:
            await message.answer(f"❌ Произошла ошибка: {e}")
            return

        if len(args) > 1:
            duration_string = args[1]
    else:
        await message.answer(
            "❌ Ответьте на сообщение или укажите @username/ID пользователя!"
        )
        return

    until_date = parse_time(duration_string)

    if duration_string and until_date is None:
        await message.answer(
            "❌ Неверно указан срок. Используйте: 30m, 2h, 1d, 1w."
        )
        return

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date,
        )

        if until_date:
            time_str = format_datetime(until_date, "%d.%m.%Y %H:%M")
            await message.answer(
                f"💜🔪 Пользователь {mention} забанен до <b>{time_str}</b>.",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                f"💜🔪 Пользователь {mention} забанен навсегда.",
                parse_mode="HTML",
            )
