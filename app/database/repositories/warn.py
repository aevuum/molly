from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.warn import Warn


class WarnRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        warn_id: str,
        user_id: int,
        chat_id: int,
        moderator_id: int,
        reason: str,
        expires_at: datetime,
        created_at: datetime,
    ) -> Warn:
        warn = Warn(
            id=warn_id,
            user_id=user_id,
            chat_id=chat_id,
            moderator_id=moderator_id,
            reason=reason,
            expires_at=expires_at,
            active=True,
            created_at=created_at,
        )

        session.add(warn)

        await session.commit()

        return warn

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        warn_id: str,
    ) -> Warn | None:
        result = await session.execute(
            select(Warn).where(
                Warn.id == warn_id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_active(
        session: AsyncSession,
        chat_id: int,
        user_id: int,
        now: datetime,
    ) -> list[Warn]:
        result = await session.execute(
            select(Warn).where(
                Warn.chat_id == chat_id,
                Warn.user_id == user_id,
                Warn.active.is_(True),
                Warn.expires_at > now,
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def remove(
        session: AsyncSession,
        warn: Warn,
        moderator_id: int,
        removed_at: datetime,
    ) -> None:
        warn.active = False
        warn.removed_at = removed_at
        warn.removed_by = moderator_id

        await session.commit()

    @staticmethod
    async def get_active_count(
        session: AsyncSession,
        chat_id: int,
        user_id: int,
        now: datetime,
    ) -> int:
        result = await session.execute(
            select(Warn).where(
                Warn.chat_id == chat_id,
                Warn.user_id == user_id,
                Warn.active.is_(True),
                Warn.expires_at > now,
            )
        )

        return len(result.scalars().all())