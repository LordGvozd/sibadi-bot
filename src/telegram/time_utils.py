import calendar
from datetime import datetime
from functools import lru_cache

from src.config import settings


@lru_cache
def get_days_in_month(date: datetime) -> int:
    month_number = date.month
    year_number = date.year

    return calendar.monthrange(year_number, month_number)[1]


@lru_cache
def find_next_monday(date: datetime) -> datetime:
    days_in_month = get_days_in_month(date)

    to_next_monday = date.day + (6 - date.weekday())

    if to_next_monday > days_in_month:
        to_next_monday -= days_in_month

    return datetime(
        year=date.year,
        month=date.month,
        day=to_next_monday,
        tzinfo=settings.timezone,
    )


@lru_cache
def get_tommorow(day: datetime) -> datetime:
    tommorow_unix = day.timestamp() + (24 * 60 * 60)
    return datetime.fromtimestamp(tommorow_unix, tz=settings.timezone)


def get_today() -> datetime:
    now = datetime.now(tz=settings.timezone)

    return now.replace(hour=0, minute=1, second=0, microsecond=1)
