from datetime import datetime
from typing import Annotated

from src.actions import (
    ActionContainer,
    LazySetting,
    TextDateParam,
    TextFromCollectionParam,
    TextParam,
)
from src.formaters import format_schedule
from src.institutions.sibadi._parser import (
    get_teacher_schedule,
    get_teachers_dict,
)

sibadi_action_container = ActionContainer()


@sibadi_action_container.action(action_id="test", display_name="Тестим :)")
def teacher_schedule_actions(
    user: Annotated[str, LazySetting("name", TextParam("имя"))],
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
        return user + "\n" + "Похоже, учитель сегодня отдыхает :)"
    
    return user + "\n" + format_schedule(schedule)
