from datetime import datetime
from functools import lru_cache
from typing import Any, Final

from src.models import Schedule
from src.parser import get_day_schedule, get_remain_week_schedule
from src.telegram.constants import SCHEDULE_KEY, ScheduleDictType
from src.telegram.time_utils import find_next_monday, get_today, get_tommorow

DAY_SCHEDULE_TEMPLATE: Final[str] = "Распорядок на: <i>{date}</i>\n"
LESSON_TEMPLATE: Final[str] = (
    "{number}) <i>[{starts_at}]</i> <b>{name}</b> <code>{audience}</code>"
)


@lru_cache
def _format_schedule(schedule: Schedule) -> str:
    head = DAY_SCHEDULE_TEMPLATE.format(date=schedule.date.strftime("%D.%m"))
    body = "\n".join([
        LESSON_TEMPLATE.format(
            number=lesson.number,
            starts_at=lesson.starts_at.strftime("%H:%M"),
            name=lesson.name.title(),
            audience=lesson.audience,
        )
        for lesson in schedule.lessons
    ])

    return head + body


@lru_cache
def _get_schedule_for_week(date: datetime) -> str:
    schedule_list = get_remain_week_schedule(date)

    if schedule_list:
        return "\n\n\n".join([_format_schedule(day) for day in schedule_list])

    return "Похоже, вы свободны до конца недели :)"


async def today_schedule_gettter(**kwargs: Any) -> ScheduleDictType:
    schedule = get_day_schedule(get_today())
    if schedule:
        return {SCHEDULE_KEY: _format_schedule(schedule)}
    return {SCHEDULE_KEY: "Похоже, сегодня нет занятий"}


async def remain_week_getter(**kwargs: Any) -> ScheduleDictType:
    return {SCHEDULE_KEY: _get_schedule_for_week(get_today())}


async def next_week_getter(**kwargs: Any) -> ScheduleDictType:
    today = get_today()
    next_monday = find_next_monday(today)
    return {SCHEDULE_KEY: _get_schedule_for_week(next_monday)}


async def tommorow_schedule_getter(**kwargs: Any) -> ScheduleDictType:
    tommorow = get_tommorow(get_today())
    schedule = get_day_schedule(tommorow)

    if schedule:
        return {SCHEDULE_KEY: _format_schedule(schedule)}

    return {SCHEDULE_KEY: "Похоже, у вас завтра нет занятий"}
