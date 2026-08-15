import asyncio
import random
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from app.database.database import async_session_factory
from app.database.models.welcome import WelcomeVerification


EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣",
    "😊", "😇", "🙂", "🙃", "😉", "😍", "🥰", "😘",
    "😋", "😛", "😜", "🤪", "🤓", "😎", "🤩", "🥳",
    "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "😣",
    "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡",
    "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰",
    "🤗", "🤔", "🤭", "🤫", "😶", "😐", "😑", "🙄",
    "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐",
    "🥴", "🤢", "🤮", "🤧", "😷", "🤒", "🤕", "🤑",
    "🤠", "😈", "👿", "🤡", "👻", "💀", "👽", "🤖",
    "🔥", "💥", "⭐", "🌟", "✨", "⚡", "💫", "🌈",
    "☀️", "🌙", "❄️", "🌊", "🍕", "🍔", "🍟", "🌭",
    "🍎", "🍉", "🍓", "🍌", "🍇", "🍒", "🥝", "🍋",
    "⚽", "🏀", "🏈", "⚾", "🎾", "🏆", "🎮", "🎯",
]


class WelcomeService:

    VERIFICATION_CHAT_ID = -1002181992075

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    async def get_verification(
        chat_id: int,
        user_id: int,
    ) -> WelcomeVerification | None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return None

        async with async_session_factory() as session:
            result = await session.execute(
                select(WelcomeVerification).where(
                    WelcomeVerification.chat_id == chat_id,
                    WelcomeVerification.user_id == user_id,
                )
            )

            return result.scalar_one_or_none()

    @staticmethod
    async def register_user(
        chat_id: int,
        user_id: int,
    ) -> None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return

        async with async_session_factory() as session:
            result = await session.execute(
                select(WelcomeVerification).where(
                    WelcomeVerification.chat_id == chat_id,
                    WelcomeVerification.user_id == user_id,
                )
            )

            verification = result.scalar_one_or_none()

            now = WelcomeService._now()

            if verification:
                verification.verified = False
                verification.correct_emoji = None
                verification.message_id = None
                verification.created_at = now
                verification.expires_at = now + timedelta(seconds=30)
            else:
                verification = WelcomeVerification(
                    chat_id=chat_id,
                    user_id=user_id,
                    verified=False,
                    created_at=now,
                    expires_at=now + timedelta(seconds=30),
                )

                session.add(verification)

            await session.commit()

    @staticmethod
    async def restrict_user(
        bot: Bot,
        chat_id: int,
        user_id: int,
    ) -> None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return

        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": False,
                "can_send_audios": False,
                "can_send_documents": False,
                "can_send_photos": False,
                "can_send_videos": False,
                "can_send_video_notes": False,
                "can_send_voice_notes": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
            },
        )

    @staticmethod
    async def restore_user(
        bot: Bot,
        chat_id: int,
        user_id: int,
    ) -> None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return

        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions={
                "can_send_messages": True,
                "can_send_audios": True,
                "can_send_documents": True,
                "can_send_photos": True,
                "can_send_videos": True,
                "can_send_video_notes": True,
                "can_send_voice_notes": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
            },
        )

    @staticmethod
    async def create_verification(
        bot: Bot,
        chat_id: int,
        user_id: int,
        first_name: str,
    ) -> None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return

        chat = await bot.get_chat(chat_id)

        if chat.type not in {"group", "supergroup"}:
            return

        emojis = random.sample(EMOJIS, 4)
        correct_emoji = random.choice(emojis)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=emoji,
                        callback_data=f"welcome:{user_id}:{emoji}",
                    )
                    for emoji in emojis
                ]
            ]
        )

        await WelcomeService.restrict_user(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
        )

        message = await bot.send_message(
            chat_id=chat_id,
            text=(
                f"👋 <a href='tg://user?id={user_id}'>"
                f"{first_name}"
                f"</a>, подтвердите, что вы человек.\n\n"
                f"🎯 Выберите эмодзи: "
                f"<b>{correct_emoji}</b>"
            ),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        async with async_session_factory() as session:
            result = await session.execute(
                select(WelcomeVerification).where(
                    WelcomeVerification.chat_id == chat_id,
                    WelcomeVerification.user_id == user_id,
                )
            )

            verification = result.scalar_one_or_none()

            if verification is None:
                return

            verification.correct_emoji = correct_emoji
            verification.message_id = message.message_id
            verification.expires_at = WelcomeService._now() + timedelta(seconds=30)

            await session.commit()

        asyncio.create_task(
            WelcomeService.verification_timeout(
                bot=bot,
                chat_id=chat_id,
                user_id=user_id,
                message_id=message.message_id,
            )
        )

    @staticmethod
    async def verify_user(
        bot: Bot,
        chat_id: int,
        user_id: int,
        emoji: str,
    ) -> bool:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return False

        async with async_session_factory() as session:
            result = await session.execute(
                select(WelcomeVerification).where(
                    WelcomeVerification.chat_id == chat_id,
                    WelcomeVerification.user_id == user_id,
                    WelcomeVerification.verified.is_(False),
                )
            )

            verification = result.scalar_one_or_none()

            if verification is None:
                return False

            if verification.expires_at <= WelcomeService._now():
                return False

            if verification.correct_emoji != emoji:
                return False

            verification.verified = True

            message_id = verification.message_id

            await session.commit()

        await WelcomeService.restore_user(
            bot=bot,
            chat_id=chat_id,
            user_id=user_id,
        )

        if message_id is not None:
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=message_id,
                )
            except TelegramBadRequest:
                pass

        return True

    @staticmethod
    async def verification_timeout(
        bot: Bot,
        chat_id: int,
        user_id: int,
        message_id: int,
    ) -> None:

        if chat_id != WelcomeService.VERIFICATION_CHAT_ID:
            return

        await asyncio.sleep(30)

        async with async_session_factory() as session:
            result = await session.execute(
                select(WelcomeVerification).where(
                    WelcomeVerification.chat_id == chat_id,
                    WelcomeVerification.user_id == user_id,
                    WelcomeVerification.verified.is_(False),
                )
            )

            verification = result.scalar_one_or_none()

            if verification is None:
                return

            if verification.expires_at > WelcomeService._now():
                return

            await session.delete(verification)
            await session.commit()

        try:
            await bot.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )

            await bot.unban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )
        except TelegramBadRequest:
            pass

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ Пользователь не прошёл проверку за 30 секунд.",
            )
        except TelegramBadRequest:
            pass