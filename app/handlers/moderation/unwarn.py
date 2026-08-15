from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.database.database import async_session_factory
from app.database.repositories.warn import WarnRepository
from app.func.time import format_datetime


unwarn_router = Router()


def make_mention(user_id: int, first_name: str | None) -> str:
    name = first_name or "пользователь"
    return f"<a href='tg://user?id={user_id}'>{name}</a>"


@unwarn_router.message(Command("unwarn"))
async def unwarn(message: Message, bot: Bot, command: CommandObject) -> None:
    if not command.args:
        await message.answer(
            "❌ Укажите ID варна.\n\n<code>/unwarn ID_варна</code>",
            parse_mode="HTML",
        )
        return

    warn_id = command.args.strip().split()[0]

    async with async_session_factory() as session:
        warn_record = await WarnRepository.get_by_id(session, warn_id)

        if warn_record is None:
            await message.answer("❌ Варн с таким ID не найден.")
            return

        if warn_record.chat_id != message.chat.id:
            await message.answer("❌ Этот варн был выдан в другом чате.")
            return

        if not warn_record.active:
            await message.answer("❌ Этот варн уже снят.")
            return

        now = datetime.now(timezone.utc)

        await WarnRepository.remove(
            session=session,
            warn=warn_record,
            moderator_id=message.from_user.id,
            removed_at=now,
        )

        active_warn_count = await WarnRepository.get_active_count(
            session=session,
            chat_id=message.chat.id,
            user_id=warn_record.user_id,
            now=now,
        )

    try:
        user = await bot.get_chat(warn_record.user_id)
        mention = make_mention(warn_record.user_id, user.first_name)
    except TelegramBadRequest:
        mention = make_mention(warn_record.user_id, "пользователь")

    expires_text = format_datetime(warn_record.expires_at)

    text = (
        f"💜✅ Варн с пользователя {mention} снят.\n\n"
        f"🆔 ID варна: <code>{warn_record.id}</code>\n"
        f"📝 Причина: <i>{warn_record.reason}</i>\n"
        f"⏱ Действовал до: {expires_text}\n"
        f"⚠️ Активных варнов: {active_warn_count}/3"
    )

    await message.answer(text, parse_mode="HTML")
