from datetime import datetime
from typing import Any, Final

import requests
from cachetools import TTLCache, cached

from src.models import Lesson, Schedule

URL_TEMPLATE: Final[str] = (
    "https://umu.sibadi.org/api/Rasp?idGroup=14720&sdate={date}"
)

cache: TTLCache[datetime, list[Schedule] | None] = TTLCache(
    maxsize=100, ttl=24 * 60 * 60
)


def _datetime_to_string(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def _parse_response_data(response_data: Any) -> list[Schedule]:
    schedule_by_day: list[Schedule] = []

    lessons_in_day: list[Lesson] = []
    current_day_date: str = ""

    for raw_lesson in response_data["data"]["rasp"]:
        if current_day_date != raw_lesson["дата"]:
            if lessons_in_day:
                schedule_by_day.append(
                    Schedule(
                        date=datetime.fromisoformat(current_day_date),
                        lessons=lessons_in_day,
                    )
                )

            lessons_in_day = []
            current_day_date = raw_lesson["дата"]

        lesson = Lesson(
            name=raw_lesson["дисциплина"],
            number=int(raw_lesson["номерЗанятия"]),
            starts_at=raw_lesson["датаНачала"],
            ends_at=raw_lesson["датаОкончания"],
            audience=raw_lesson["аудитория"],
        )
        lessons_in_day.append(lesson)

    return schedule_by_day


@cached(cache)
def get_remain_week_schedule(date: datetime) -> list[Schedule] | None:
    """Получает расписание на оставшуююся неделю."""
    formatted_datetime = _datetime_to_string(date)

    response = requests.get(
        URL_TEMPLATE.format(date=formatted_datetime), timeout=5
    )

    response_data = response.json()

    return _parse_response_data(response_data)


def get_day_schedule(date: datetime) -> Schedule | None:
    """Получает расписание с сайта."""
    schedule_by_days = get_remain_week_schedule(date)

    if not schedule_by_days:
        return None

    for day in schedule_by_days:
        if day.date.day == date.day:
            return day
    return None
