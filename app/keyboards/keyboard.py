from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote

CHAT_URL = "https://t.me/mollyfest_chat"
RULES_URL = "https://telegra.ph/Pravila-chata-MOLLY-FEST-08-14"
FAQ_URL = "https://telegra.ph/Otvety-na-voprosy-MOLLY-FEST-08-19"

encoded_faq_url = quote(FAQ_URL)
IN_APP_FAQ_URL = f"https://t.me/iv?url={encoded_faq_url}&rhash=00000000000000"

channel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🗨️ ЧАТ", url=CHAT_URL),
            InlineKeyboardButton(text="ПРАВИЛА 📚", url=RULES_URL),
        ],
        [InlineKeyboardButton(text="⁉️ ОТВЕТЫ НА ВОПРОСЫ ⁉️", url=FAQ_URL)],
    ]
)
