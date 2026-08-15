from contextlib import suppress
from typing import Any

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import ChatPermissions, Message

from app.func.parseTime import parse_time
from app.func.time import format_datetime


mute_router = Router()


def _parse_target(command: CommandObject | None) -> tuple[str | None, str | None]:
    if not command or not command.args:
        return None, None

    parts = command.args.strip().split()
    if not parts:
        return None, None

    return parts[0], parts[1] if len(parts) > 1 else None


async def _resolve_target(message: Message, bot: Bot, target: str | None):
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        return user.id, f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    if not target:
        await message.answer(
            "❌ Ответьте на сообщение или укажите @username/ID пользователя!"
        )
        return None

    if target.startswith("@"):
        try:
            user = await bot.get_chat(target)
        except TelegramBadRequest:
            await message.answer(f"❌ Пользователь {target} не найден.")
            return None

        name = user.first_name or user.username or "пользователь"
        return user.id, f"<a href='tg://user?id={user.id}'>{name}</a>"

    try:
        user_id = int(target)
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Используйте @username или числовой ID."
        )
        return None

    try:
        user = await bot.get_chat(user_id)
        name = user.first_name or user.username or "пользователь"
    except TelegramBadRequest:
        name = "пользователь"

    return user_id, f"<a href='tg://user?id={user_id}'>{name}</a>"


@mute_router.message(Command("mute"))
async def mute(
    message: Message,
    bot: Bot,
    command: CommandObject | None = None,
) -> Any:
    target, duration_string = _parse_target(command)
    resolved = await _resolve_target(message, bot, target)

    if resolved is None:
        return

    if message.reply_to_message and command and command.args:
        duration_string = command.args.strip().split()[0]

    if not duration_string:
        await message.answer(
            "❌ Укажите срок мута: 30m, 2h, 1d, 1w."
        )
        return

    until_date = parse_time(duration_string)
    if until_date is None:
        await message.answer(
            "❌ Неверно указан срок. Используйте: 30m, 2h, 1d, 1w."
        )
        return

    user_id, mention = resolved

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date,
            permissions=ChatPermissions(can_send_messages=False),
        )

        time_str = format_datetime(until_date)
        await message.answer(
            f"💜🔇 Пользователь {mention} замучен до <b>{time_str}</b>.",
            parse_mode="HTML",
        )


@mute_router.message(Command("unmute"))
async def unmute(
    message: Message,
    bot: Bot,
    command: CommandObject | None = None,
) -> Any:
    target = command.args.strip().split()[0] if command and command.args else None
    resolved = await _resolve_target(message, bot, target)

    if resolved is None:
        return

    user_id, mention = resolved

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False,
            ),
        )

        await message.answer(
            f"💜🔊 Пользователь {mention} размучен.",
            parse_mode="HTML",
        )
