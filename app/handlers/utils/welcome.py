import asyncio
import random

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


welcome_router = Router()

pending_users: dict[tuple[int, int], asyncio.Task] = {}


EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣",
    "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰",
    "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜",
    "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏",
    "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣",
    "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠",
    "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨",
    "😰", "😥", "😓", "🤗", "🤔", "🫡", "🤭", "🤫",
    "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦",
    "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵",
    "🤐", "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕",
    "🤑", "🤠", "😈", "👿", "👹", "👺", "🤡", "💩",
    "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "😺",
    "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾",
    "🔥", "💥", "⭐", "🌟", "✨", "⚡", "💫", "🌈",
    "☀️", "🌙", "❄️", "🌊", "🍕", "🍔", "🍟", "🌭",
    "🍎", "🍉", "🍓", "🍌", "🍇", "🍒", "🥝", "🍋",
    "⚽", "🏀", "🏈", "⚾", "🎾", "🏆", "🎮", "🎯",
]


def create_emoji_keyboard(
    user_id: int,
) -> tuple[InlineKeyboardMarkup, list[str]]:
    emojis = random.sample(EMOJIS, 4)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=emoji,
                    callback_data=f"verify:{user_id}:{emoji}",
                )
                for emoji in emojis
            ]
        ]
    )

    return keyboard, emojis


@welcome_router.chat_member(
    F.new_chat_member.status == "member"
)
async def welcome_new_member(
    event: ChatMemberUpdated,
    bot: Bot,
) -> None:
    user = event.new_chat_member.user

    if user.is_bot:
        return

    chat_id = event.chat.id
    user_id = user.id

    keyboard, emojis = create_emoji_keyboard(user_id)

    correct_emoji = random.choice(emojis)

    message = await bot.send_message(
        chat_id=chat_id,
        text=(
            f"💜👋 Добро пожаловать, готов веселиться?"
            f"<a href='tg://user?id={user_id}'>{user.first_name}</a>!\n\n"
            f"💜🎯 Выберите эмодзи <b>{correct_emoji}</b> "
            "в течение 30 секунд:"
        ),
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    task = asyncio.create_task(
        verification_timeout(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
            message_id=message.message_id,
        )
    )

    pending_users[(chat_id, user_id)] = task

    pending_users[(chat_id, user_id, "correct")] = correct_emoji


async def verification_timeout(
    bot: Bot,
    chat_id: int,
    user_id: int,
    message_id: int,
) -> None:
    try:
        await asyncio.sleep(30)

        key = (chat_id, user_id)

        if key not in pending_users:
            return

        pending_users.pop(key, None)
        pending_users.pop(
            (chat_id, user_id, "correct"),
            None,
        )

        try:
            await bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    "💜❌ Пользователь не прошёл проверку "
                    "за 30 секунд и был удалён."
                ),
            )

        except TelegramBadRequest:
            pass

    except asyncio.CancelledError:
        return


@welcome_router.callback_query(
    F.data.startswith("verify:")
)
async def verify_user(
    callback: CallbackQuery,
) -> None:
    if not callback.data:
        return

    _, user_id_string, emoji = callback.data.split(
        ":",
        2,
    )

    user_id = int(user_id_string)

    if callback.from_user.id != user_id:
        await callback.answer(
            "💜❌ Эта проверка предназначена не для вас.",
            show_alert=True,
        )
        return

    chat_id = callback.message.chat.id

    key = (chat_id, user_id)
    correct_key = (
        chat_id,
        user_id,
        "correct",
    )

    correct_emoji = pending_users.get(
        correct_key
    )

    if correct_emoji is None:
        await callback.answer(
            "💜❌ Время проверки истекло.",
            show_alert=True,
        )
        return

    if emoji != correct_emoji:
        await callback.answer(
            "💜❌ Неверный эмодзи!",
            show_alert=True,
        )
        return

    task = pending_users.pop(
        key,
        None,
    )

    pending_users.pop(
        correct_key,
        None,
    )

    if task is not None:
        task.cancel()

    await callback.answer(
        "💜✅ Проверка пройдена!"
    )

    await callback.message.edit_text(
        f"💜✅ {callback.from_user.first_name} "
        f"прошёл проверку."
    )