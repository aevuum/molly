from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


async def get_user_by_username_or_id(
    bot: Bot, chat_id: int, identifier: str
) -> tuple[int, str]:
    try:
        if identifier.isdigit():
            user_id = int(identifier)
            mention = f"<a href='tg://user?id={user_id}'>пользователь</a>"
            return user_id, mention
        username = identifier.lstrip("@").lower()
        administrators = await bot.get_chat_administrators(chat_id)
        for admin in administrators:
            if admin.user.username and admin.user.username.lower() == username:
                user_id = admin.user.id
                user_name = admin.user.first_name or admin.user.username
                mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
                return user_id, mention

        try:
            user = await bot.get_chat(f"@{username}")
            user_id = user.id
            user_name = user.first_name or user.username or username
            mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
            try:
                await bot.get_chat_member(chat_id, user_id)
                return user_id, mention
            except TelegramBadRequest:
                raise ValueError(f"Пользователь @{username} не найден в этом чате")

        except TelegramBadRequest:
            raise ValueError(f"Пользователь @{username} не найден")

    except Exception as e:
        raise Exception(f"Ошибка при получении пользователя: {e}")
