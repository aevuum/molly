from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.database.models.warn import Warn

__all__ = [
    "Base",
    "Warn",
]