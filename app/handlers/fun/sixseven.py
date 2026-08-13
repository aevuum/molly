from aiogram import Router, F
from aiogram.types import Message, FSInputFile


sixseven_router = Router()


@sixseven_router.message(
    F.text.lower().contains("сиксевен")
)
async def sixseven(message: Message) -> None:
    await message.answer("сиксевен")

    gif = FSInputFile(
        "app/assets/sixseven.gif"
    )

    await message.answer(
    "сиксевен"
)

    await message.answer_animation(
        animation=gif,
        reply_to_message_id=message.message_id
    )