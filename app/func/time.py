from datetime import datetime, timezone
from zoneinfo import ZoneInfo


DISPLAY_TIMEZONE = ZoneInfo("Europe/Moscow")


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def format_datetime(value: datetime, fmt: str = "%d.%m %H:%M") -> str:
    return ensure_utc(value).astimezone(DISPLAY_TIMEZONE).strftime(fmt)
