from typing import Annotated

from src.actions import ActionContainer, RequireStudent, TextParam
from src.institutions.sibadi.student import SibadiStudent

sibadi_action_container = ActionContainer()


@sibadi_action_container.action(action_id="test", display_name="Тестим :)")
def test_action(
    student: Annotated[SibadiStudent, RequireStudent()],
    text: Annotated[str, TextParam("текст, который скажет студент")],
) -> str:
    return f"Студент из {student.group_id} говорит: {text}"
