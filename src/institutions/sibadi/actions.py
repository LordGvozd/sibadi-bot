from typing import Annotated

from src.actions import (
    ActionContainer,
    ChoiceParam,
    RequireStudent,
    TextFromCollectionParam,
    TextParam,
)
from src.institutions.sibadi.student import SibadiStudent

sibadi_action_container = ActionContainer()


@sibadi_action_container.action(action_id="test", display_name="Тестим :)")
def test_action(
    student: Annotated[SibadiStudent, RequireStudent()],
    fruit: Annotated[
        str,
        TextFromCollectionParam(
            "фрукт, который любит студент",
            collection=["банан", "яблоко", "кукуруз", "арбуз", "помидор"],
        ),
    ],
    mood: Annotated[str, ChoiceParam("настроение студента", variants=["хорошее", "плохое", "я это все джага джага"])],
    text: Annotated[str, TextParam("текст, который скажет студент")],
) -> str:
    return f"Студент из {student.group_id}, его настроение '{mood}', любит {fruit}, и говорит: {text}"
