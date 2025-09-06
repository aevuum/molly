from aiogram import Router
from aiogram.types import Message, FSInputFile
import app.keyboards.keyboard as kb
import asyncio

channel = Router()

SOURCE_CHANNEL_ID = -1002238628633
DISCUSSION_CHAT_ID = -1002181992075
PATH_TO_PICTURE = "app/photo/paranoya.jpg"

CUSTOM_EMOJI = [5201793419428521041, 5199954859893225524, 5199594366108203245]

CAPTION = (
    "<tg-emoji emoji-id='{emoji_0}'>🎉</tg-emoji> Подписчик, соблюдай правила, указанные ниже.\n\n"
    "<tg-emoji emoji-id='{emoji_1}'>❓</tg-emoji> Появился вопрос? Снизу есть ответ в FAQ.\n\n"
    "<tg-emoji emoji-id='{emoji_2}'>📧</tg-emoji> Также у нас есть свой чат, где вы можете найти компанию на концерт!"
).format(emoji_0=CUSTOM_EMOJI[0], emoji_1=CUSTOM_EMOJI[1], emoji_2=CUSTOM_EMOJI[2])

CHANNEL_PHOTO = FSInputFile(PATH_TO_PICTURE)


@channel.message()
async def handle_discussion_message(message: Message):
    if (
        message.chat.id == DISCUSSION_CHAT_ID
        and message.forward_from_chat
        and message.forward_from_chat.id == SOURCE_CHANNEL_ID
    ):

        await asyncio.sleep(3)

        await message.bot.send_photo(
            chat_id=DISCUSSION_CHAT_ID,
            photo=CHANNEL_PHOTO,
            caption=CAPTION,
            parse_mode="HTML",
            reply_markup=kb.channel_keyboard,
            reply_to_message_id=message.message_id,
        )
