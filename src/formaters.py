from datetime import time
from typing import Final

from src.models import Schedule

DAY_SCHEDULE_TEMPLATE: Final[str] = "Распорядок на: <i>{date}</i>\n"
LESSON_TEMPLATE: Final[str] = (
    "{number}) <i>[{starts_at}]</i> <b>{name}</b> <code>{audience}</code>"
)
LESSON_TIME_TEMPLATE: Final[str] = "{number}) {starts_at}-{ends_at}\n"


def format_timetable(timetable: tuple[tuple[time, time], ...]) -> str:
    text = ""

    for index, lesson in enumerate(timetable):  # noqa: WPS519
        starts_at = f"{lesson[0].hour}:{lesson[0].minute}"
        ends_at = f"{lesson[1].hour}:{lesson[1].minute}"

        text += LESSON_TEMPLATE.format(
            number=index + 1, starts_at=starts_at, ends_at=ends_at
        )

    return text


def format_schedule(schedule: Schedule | None) -> str:
    if not schedule:
        return "У вас нет занятий на этот день!"

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


def format_schedule_for_week(schedule_list: list[Schedule] | None) -> str:
    if schedule_list:
        return "\n\n\n".join([format_schedule(day) for day in schedule_list])

    return "Похоже, вы свободны до конца недели :)"
