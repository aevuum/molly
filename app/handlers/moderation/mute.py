from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ChatPermissions
from typing import Any
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from app.func.parseTime import parse_time

mute_router = Router()


@mute_router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
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

    until_date = parse_time(command.args)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False,
            ),
        )

        time_str = until_date.strftime("%d.%m.%Y %H:%M")
        await message.answer(
            f"💜🔇 Пользователь {mention} замучен до <b>{time_str}</b>.",
            parse_mode="HTML",
        )


@mute_router.message(Command("unmute"))
async def unmute(
    message: Message, bot: Bot, command: CommandObject | None = None
) -> Any:
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
