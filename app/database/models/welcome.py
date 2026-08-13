from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base


class WelcomeVerification(Base):
    __tablename__ = "welcome_verifications"

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "user_id",
            name="uq_welcome_verification_chat_user",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
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

    verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    correct_emoji: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )