from typing import Annotated

from src.actions import (
    ActionContainer,
    ChoiceParam,
    RequireStudent,
    TextFromCollectionParam,
)
from src.institutions.sibadi._parser import get_teachers_dict
from src.institutions.sibadi.student import SibadiStudent

sibadi_action_container = ActionContainer()


@sibadi_action_container.action(action_id="test", display_name="Тестим :)")
def get_teacher_schedule(
    teacher: Annotated[
        str,
        TextFromCollectionParam(
            "ФИО учителя", tuple(get_teachers_dict().keys())
        ),
    ],
    period: Annotated[
        str, ChoiceParam("период", ["сегодня", "неделя", "следущяя неделя"])
    ],
) -> str:
    return "OK os"
