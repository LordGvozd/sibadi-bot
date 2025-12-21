from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.abstractions import Institution, InstitutionNames
from src.actions import Action, Param
from src.institutions.sibadi.student import SibadiStudent
from src.institutions.types import AnyStudent
from src.telegram.common import aviable_institutions


async def get_action_from_state(
    msg: Message, state: FSMContext
) -> Action | None:
    action_id = await state.get_value("action_id")
    if action_id is None:
        return None

    inst = await get_inst_from_state(msg, state)
    return inst.action_container.get_action(action_id)


async def get_current_param_from_state(
    msg: Message, state: FSMContext
) -> tuple[str, Param]:
    action = await get_action_from_state(msg, state)

    current_param_name = await state.get_value("current_param_name")
    if not current_param_name:
        raise Exception

    action = await get_action_from_state(msg, state)

    if not action:
        raise Exception

    current_param_type = action.get_params()[current_param_name]

    return str(current_param_name), current_param_type


async def get_inst_from_state(msg: Message, state: FSMContext) -> Institution:
    inst_raw = await state.get_value("inst")

    if not isinstance(inst_raw, str):
        await msg.answer("у вас не выбрано учебное заведение. Введите /start!")
        raise Exception

    return aviable_institutions[InstitutionNames(inst_raw)]


async def get_student_from_state(tg_id: int, state: FSMContext) -> AnyStudent:
    inst = await state.get_value("inst")
    match InstitutionNames(str(inst)):
        case InstitutionNames.SIBADI:
            group_id = await state.get_value("group_id")

            if not group_id:
                raise ValueError

            return SibadiStudent(tg_id=str(tg_id), group_id=group_id)
