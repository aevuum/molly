from datetime import datetime, timedelta, timezone
import re


TIMEZONE = timezone.utc


def now_utc() -> datetime:
    return datetime.now(TIMEZONE)


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None

    match_ = re.fullmatch(
        r"(\d+)([mhdw])",
        time_string.lower().strip(),
    )

    if not match_:
        return None

    value = int(match_.group(1))
    unit = match_.group(2)

    match unit:
        case "m":
            time_delta = timedelta(minutes=value)
        case "h":
            time_delta = timedelta(hours=value)
        case "d":
            time_delta = timedelta(days=value)
        case "w":
            time_delta = timedelta(weeks=value)
        case _:
            return None

    return now_utc() + time_delta
