from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from typing import Any
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress
from app.func.getUserByIdOrUsername import get_user_by_username_or_id

kick_router = Router()


@kick_router.message(Command("kick"), F.chat.type.in_({"supergroup", "group"}))
async def kick_func(message: Message, bot: Bot, command: CommandObject) -> Any:
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

        target = args[0]

        try:
            # Импортируем функцию получения пользователя

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

    # Получаем причину (если есть)
    reason = (
        " ".join(command.args.split()[1:])
        if command and command.args and len(command.args.split()) > 1
        else "Не указана"
    )

    with suppress(TelegramBadRequest):
        # Кикаем пользователя
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)

        # Сразу разбаниваем, чтобы он мог вернуться
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=user_id)

        await message.answer(
            f"🚪 Пользователь {mention} был кикнут\n📝 Причина: {reason}",
            parse_mode="HTML",
        )
