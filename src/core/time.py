from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def now_moscow() -> datetime:
    return datetime.now(MOSCOW_TZ)


def one_hour_from_now_moscow() -> datetime:
    return (now_moscow() + timedelta(hours=1)).replace(second=0, microsecond=0)


def days_ago_moscow(days: int) -> datetime:
    return now_moscow() - timedelta(days=days)
