from datetime import datetime
from functools import lru_cache
import calendar
from typing import Literal


from src.models import Schedule
from src.parser import get_day_schedule, get_remain_week_schedule


@lru_cache
def _format_schedule(schedule: Schedule) -> str:
    head = f"распорядок на: <i>{schedule.date.strftime('%d-%m-%Y')}</i>\n\n"

    body = "\n".join([
        f"{lesson.number}) <i>[{lesson.starts_at.strftime('%H:%M')}]</i> <b>{lesson.name.title()}</b> <code>{lesson.audience}</code>"
        for lesson in schedule.lessons
    ])

    return head + body


@lru_cache
def _get_days_in_month(date: datetime) -> int:
    month_number = date.month
    year_number = date.year

    return calendar.monthrange(year_number, month_number)[1]


@lru_cache
def _find_next_monday(date: datetime) -> datetime:
    days_in_month = _get_days_in_month(date)

    to_next_monday = date.day + (6 - date.weekday())

    if to_next_monday > days_in_month:
        to_next_monday -= days_in_month

    monday = datetime(year=date.year, month=date.month, day=to_next_monday)

    return monday

@lru_cache
def _get_schedule_for_week(date: datetime) -> str:
    schedule_list = get_remain_week_schedule(date)

    if schedule_list:
        answer_text = "\n\n\n".join([
            _format_schedule(day) for day in schedule_list
        ])

        return answer_text
    return "Похоже, вы свободны до конца недели :)"


def get_today() -> datetime:
    now = datetime.now()

    return now.replace(hour=0, minute=1, second=0, microsecond=1)

@lru_cache
def get_tommorow(day: datetime) -> datetime:
    tommorow_unix = day.timestamp() + (24 * 60 * 60)
    return datetime.fromtimestamp(tommorow_unix)



async def today_schedule_gettter(**kwargs) -> dict[Literal["schedule"], str]:
    schedule = get_day_schedule(get_today())
    if schedule:
        return {"schedule": _format_schedule(schedule)}
    return {"schedule": "Похоже, сегодня нет занятий"}


async def remain_week_getter(**kwargs) -> dict[Literal["schedule"], str]:
    return {"schedule": _get_schedule_for_week(get_today())}


async def next_week_getter(**kwargs) -> dict[Literal["schedule"], str]:
    today = get_today()
    next_monday = _find_next_monday(today)
    return {"schedule": _get_schedule_for_week(next_monday)}


async def tommorow_schedule_getter(**kwargs) -> dict[Literal["schedule"], str]:
    tommorow = get_tommorow(get_today())
    schedule = get_day_schedule(tommorow)

    if schedule:
        return {"schedule": _format_schedule(schedule)}
       
    return {"schedule": "Похоже, у вас завтра нет занятий"}
    

