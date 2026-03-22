from datetime import datetime, timedelta, timezone


def now_utc_plus_3() -> datetime:
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=3)))


def one_hour_from_now_utc_plus_3() -> datetime:
    return (now_utc_plus_3() + timedelta(hours=1))


def days_ago_utc_plus_3(days: int) -> datetime:
    return now_utc_plus_3() - timedelta(days=days)
