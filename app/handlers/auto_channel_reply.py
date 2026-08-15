import asyncio

from aiogram import Router
from aiogram.types import FSInputFile, Message

import app.keyboards.keyboard as kb


channel = Router()

SOURCE_CHANNEL_ID = -1002238628633
DISCUSSION_CHAT_ID = -1002181992075
PATH_TO_PICTURE = "app/photo/paranoya.jpg"

CUSTOM_EMOJI = [
    5201793419428521041,
    5199954859893225524,
    5199594366108203245,
]

CAPTION = (
    "<tg-emoji emoji-id='{emoji_0}'>🎉</tg-emoji> "
    "Подписчик, соблюдай правила, указанные ниже.\n\n"
    "<tg-emoji emoji-id='{emoji_1}'>❓</tg-emoji> "
    "Появился вопрос? Снизу есть ответ в FAQ.\n\n"
    "<tg-emoji emoji-id='{emoji_2}'>📧</tg-emoji> "
    "Также у нас есть свой чат, где вы можете найти компанию на концерт!"
).format(
    emoji_0=CUSTOM_EMOJI[0],
    emoji_1=CUSTOM_EMOJI[1],
    emoji_2=CUSTOM_EMOJI[2],
)

CHANNEL_PHOTO = FSInputFile(PATH_TO_PICTURE)


def is_channel_post_in_discussion(message: Message) -> bool:
    if message.chat.id != DISCUSSION_CHAT_ID:
        return False

    # Telegram пересылает публикацию из канала в linked discussion
    # как automatic forward. В aiogram 3.30 надёжнее проверять
    # sender_chat + is_automatic_forward, а не старый forward_from_chat.
    if not message.is_automatic_forward:
        return False

    if not message.sender_chat:
        return False

    return message.sender_chat.id == SOURCE_CHANNEL_ID


@channel.message()
async def handle_discussion_message(message: Message):
    if not is_channel_post_in_discussion(message):
        return

    await asyncio.sleep(3)

    try:
        await message.bot.send_photo(
            chat_id=DISCUSSION_CHAT_ID,
            photo=CHANNEL_PHOTO,
            caption=CAPTION,
            parse_mode="HTML",
            reply_markup=kb.channel_keyboard,
            reply_to_message_id=message.message_id,
        )
    except Exception:
        # Не роняем polling, если пост уже удалён/обсуждение недоступно.
        return
