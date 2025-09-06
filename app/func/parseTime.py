from datetime import datetime, timedelta
import re


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None
    match_ = re.match(r"(\d+)([a-z])", time_string.lower().strip())
    if not match_:
        return None
    value, unit = int(match_.group(1)), match_.group(2)
    current_datetime = datetime.now()
    match unit:
        case "h":
            time_delta = timedelta(hours=value)
        case "d":
            time_delta = timedelta(days=value)
        case "w":
            time_delta = timedelta(weeks=value)
        case "m":
            time_delta = timedelta(minutes=value)
        case _:
            return None
    return current_datetime + time_delta
