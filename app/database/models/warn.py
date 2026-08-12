from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models import Base


class Warn(Base):
    __tablename__ = "warns"

    id: Mapped[str] = mapped_column(
        String(24),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    moderator_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    removed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    removed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )