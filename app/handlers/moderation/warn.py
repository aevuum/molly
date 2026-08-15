import secrets
from contextlib import suppress
from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.database.database import async_session_factory
from app.database.repositories.warn import WarnRepository
from app.func.parseTime import parse_time
from app.func.time import format_datetime


warn_router = Router()


def make_mention(user_id: int, first_name: str | None) -> str:
    name = first_name or "пользователь"
    return f"<a href='tg://user?id={user_id}'>{name}</a>"


async def resolve_user(message: Message, bot: Bot, target: str | None):
    if target is None:
        if not message.reply_to_message or not message.reply_to_message.from_user:
            await message.answer(
                "❌ Ответьте на сообщение пользователя или укажите @username/ID."
            )
            return None

        user = message.reply_to_message.from_user
        return user.id, make_mention(user.id, user.first_name)

    if target.startswith("@"):
        try:
            user = await bot.get_chat(target)
        except TelegramBadRequest:
            await message.answer(f"❌ Пользователь {target} не найден.")
            return None

        return user.id, make_mention(user.id, user.first_name)

    try:
        user_id = int(target)
    except ValueError:
        await message.answer(
            "❌ Неверный формат пользователя. Используйте @username или числовой ID."
        )
        return None

    try:
        user = await bot.get_chat(user_id)
        first_name = user.first_name
    except TelegramBadRequest:
        first_name = "пользователь"

    return user_id, make_mention(user_id, first_name)


def parse_warn_command(args: str) -> tuple[str | None, str, str]:
    parts = args.strip().split()

    if not parts:
        raise ValueError("Укажите срок и причину варна.")

    if parse_time(parts[0]) is not None:
        target = None
        duration_string = parts[0]
        reason_start = 1
    else:
        if len(parts) < 2:
            raise ValueError("Укажите срок и причину варна.")

        target = parts[0]
        duration_string = parts[1]

        if parse_time(duration_string) is None:
            raise ValueError("Неверно указан срок варна.")

        reason_start = 2

    if len(parts) <= reason_start:
        raise ValueError("Укажите причину варна.")

    reason = " ".join(parts[reason_start:]).strip()
    if not reason:
        raise ValueError("Укажите причину варна.")

    return target, duration_string, reason


@warn_router.message(Command("warn"))
async def warn(message: Message, bot: Bot, command: CommandObject) -> None:
    if not command.args:
        await message.answer(
            "❌ Использование:\n\n"
            "<code>/warn 1w причина</code> — ответом на сообщение\n"
            "<code>/warn @username 1w причина</code>\n"
            "<code>/warn 123456789 1w причина</code>",
            parse_mode="HTML",
        )
        return

    try:
        target, duration_string, reason = parse_warn_command(command.args)
    except ValueError as error:
        await message.answer(f"❌ {error}")
        return

    expires_at = parse_time(duration_string)
    if expires_at is None:
        await message.answer("❌ Неверно указан срок варна.")
        return

    resolved = await resolve_user(message, bot, target)
    if resolved is None:
        return

    user_id, mention = resolved

    if user_id == message.from_user.id:
        await message.answer("❌ Нельзя выдать варн самому себе.")
        return

    with suppress(TelegramBadRequest):
        member = await bot.get_chat_member(message.chat.id, user_id)
        if member.user.is_bot:
            await message.answer("❌ Нельзя выдать варн боту.")
            return

    now = datetime.now(timezone.utc)

    async with async_session_factory() as session:
        active_warns = await WarnRepository.get_active(
            session=session,
            chat_id=message.chat.id,
            user_id=user_id,
            now=now,
        )

        warn_id = secrets.token_hex(12)

        await WarnRepository.create(
            session=session,
            warn_id=warn_id,
            user_id=user_id,
            chat_id=message.chat.id,
            moderator_id=message.from_user.id,
            reason=reason,
            expires_at=expires_at,
            created_at=now,
        )

        active_warn_count = len(active_warns) + 1

    expires_text = format_datetime(expires_at)

    text = (
        f"💜⚠️ {mention} получил варн "
        f"({active_warn_count}/3) "
        f"(действует до {expires_text})\n"
        f"Причина: <i>{reason}</i>\n"
        f"ID варна: <code>{warn_id}</code>"
    )

    if active_warn_count >= 3:
        try:
            await bot.ban_chat_member(
                chat_id=message.chat.id,
                user_id=user_id,
            )
            text += "\n\n🚫 Пользователь получил 3 активных варна и был заблокирован."
        except TelegramBadRequest:
            text += "\n\n⚠️ Достигнуто 3 активных варна, но заблокировать пользователя не удалось."

    await message.answer(text, parse_mode="HTML")
