from datetime import datetime, time
from typing import Annotated

from src.actions import (
    ActionContainer,
    LazySetting,
    TextDateParam,
    TextFromCollectionParam,
    TextParam,
)
from src.formaters import format_schedule, format_timetable
from src.institutions.sibadi._parser import (
    get_teacher_schedule,
    get_teachers_dict,
)
sibadi_action_container = ActionContainer()


@sibadi_action_container.action(action_id="teac_schedu", display_name="Расписание учителя")
def teacher_schedule_actions(
    teacher: Annotated[
        str,
        TextFromCollectionParam(
            "ФИО учителя", tuple(get_teachers_dict().keys())
        ),
    ],
    date: Annotated[datetime, TextDateParam("интересующюю вас дата")],
) -> str:
    schedule = get_teacher_schedule(
        teacher_id=get_teachers_dict()[teacher], date=date
    )

    if schedule is None:
        return "Похоже, учитель сегодня отдыхает :)"

    return format_schedule(schedule)

@sibadi_action_container.action(action_id="time", display_name="Звонки")
def times_actions() -> str:
    return format_timetable((
        (time(8, 20), time(9, 50)),  # noqa: WPS432
        (time(10, 00), time(11, 30)),  # noqa: WPS432
        (time(11, 40), time(13, 10)),  # noqa: WPS432
        (time(13, 45), time(15, 15)),  # noqa: WPS432
        (time(15, 25), time(16, 55)),  # noqa: WPS432
        (time(17, 5), time(18, 35)),  # noqa: WPS432

    ))
