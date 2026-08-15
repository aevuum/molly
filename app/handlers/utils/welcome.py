from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, ChatMemberUpdated

from app.services.welcome import WelcomeService, VERIFICATION_CHAT_ID


welcome_router = Router()


@welcome_router.chat_member(
    F.new_chat_member.status == "member"
)
async def user_joined(
    event: ChatMemberUpdated,
    bot: Bot,
) -> None:

    # Капча работает только в linked discussion group.
    # Даже если бот также добавлен в сам канал, там ничего не происходит.
    if event.chat.id != VERIFICATION_CHAT_ID:
        return

    if event.chat.type not in {"group", "supergroup"}:
        return

    user = event.new_chat_member.user

    if user.is_bot:
        return

    await WelcomeService.register_user(
        chat_id=event.chat.id,
        user_id=user.id,
    )

    # Отправляем капчу сразу после входа, а не ждём первого сообщения.
    await WelcomeService.create_verification(
        bot=bot,
        chat_id=event.chat.id,
        user_id=user.id,
        first_name=user.first_name,
    )


@welcome_router.callback_query(
    F.data.startswith("welcome:")
)
async def verify_welcome(
    callback: CallbackQuery,
    bot: Bot,
) -> None:

    if not callback.message:
        return

    if callback.message.chat.id != VERIFICATION_CHAT_ID:
        await callback.answer()
        return

    if callback.message.chat.type not in {"group", "supergroup"}:
        await callback.answer()
        return

    if not callback.data:
        return

    _, user_id_string, emoji = callback.data.split(":", 2)

    user_id = int(user_id_string)

    if callback.from_user.id != user_id:
        await callback.answer(
            "❌ Эта проверка предназначена не для вас.",
            show_alert=True,
        )
        return

    success = await WelcomeService.verify_user(
        bot=bot,
        chat_id=callback.message.chat.id,
        user_id=user_id,
        emoji=emoji,
    )

    if not success:
        await callback.answer(
            "❌ Неверный эмодзи или время проверки истекло.",
            show_alert=True,
        )
        return

    await callback.answer("✅ Проверка пройдена!")

    try:
        await callback.message.edit_text(
            f"✅ <a href='tg://user?id={user_id}'>"
            f"{callback.from_user.first_name}"
            f"</a> прошёл проверку.",
            parse_mode="HTML",
        )
    except Exception:
        pass
