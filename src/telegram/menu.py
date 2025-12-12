from typing import Any
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.abstractions import Institution, InstitutionNames
from src.actions import Action, TextParam
from src.formaters import (
    format_schedule,
    format_schedule_for_week,
)
from src.institutions.sibadi.sibadi import Sibadi, SibadiStudent
from src.institutions.types import AnyStudent
from src.telegram.time_utils import find_next_monday, get_today, get_tommorow

institutions = {InstitutionNames.SIBADI.value: Sibadi()}


class BaseStates(StatesGroup):
    main = State()


main_router = Router()
back_to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="menu")]]
)


async def open_menu(msg: Message, state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()
    builder.max_width = 1

    builder.button(text="Сегодня", callback_data="today")
    builder.button(text="Завтра", callback_data="tommorow")
    builder.button(text="Неделя", callback_data="remain_week")
    builder.button(text="Следущяя неделя", callback_data="next_week")
    builder.button(text="Звонки", callback_data="time")
    builder.button(text="Действия", callback_data="action")

    await state.set_state(BaseStates.main)
    await msg.edit_text(
        text="Привет! Это меню.", reply_markup=builder.as_markup()
    )


async def _edit_msg_to_action(text: str, msg: Message) -> None:
    await msg.edit_text(text=text, reply_markup=back_to_menu_kb)


async def _get_student_from_state(tg_id: int, state: FSMContext) -> AnyStudent:
    inst = await state.get_value("inst")
    match InstitutionNames(str(inst)):
        case InstitutionNames.SIBADI:
            group_id = await state.get_value("group_id")

            if not group_id:
                raise ValueError

            return SibadiStudent(tg_id=str(tg_id), group_id=group_id)


def _get_msg(query: CallbackQuery) -> Message:
    if isinstance(query.message, Message):
        return query.message
    raise Exception("Some error with query!")


@main_router.callback_query(F.data == "menu")
async def proceess_menu(query: CallbackQuery, state: FSMContext) -> None:
    await open_menu(_get_msg(query), state)


class ActionState(StatesGroup):
    set_params = State()


@main_router.callback_query(F.data == "action")
async def open_action_menu(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)
    inst_raw = await state.get_value("inst")

    if not isinstance(inst_raw, str):
        await msg.answer("у вас не выбрано учебное заведение. Введите /start!")
        return

    inst = institutions[InstitutionNames(inst_raw)]

    builder = InlineKeyboardBuilder()
    builder.max_width = 1

    if len(inst.action_container.actions) == 0:
        await msg.edit_text("Нет действий!")
        return

    for action_id, action in inst.action_container.actions.items():
        builder.button(text=action.display_name, callback_data=f"a.{action_id}")

    builder.button(text="Меню", callback_data="menu")

    await state.set_state(BaseStates.main)
    await msg.edit_text(
        text="Привет! Это меню.", reply_markup=builder.as_markup()
    )


async def _get_acion_from_state(
    action_id: str, msg: Message, state: FSMContext
) -> Action | None:
    inst = await _get_inst_from_state(msg, state)
    return inst.action_container.get_action(action_id)


async def _get_inst_from_state(msg: Message, state: FSMContext) -> Institution:
    inst_raw = await state.get_value("inst")

    if not isinstance(inst_raw, str):
        await msg.answer("у вас не выбрано учебное заведение. Введите /start!")
        raise Exception

    return institutions[InstitutionNames(inst_raw)]


async def _render_action_result(
    action: Action, student: AnyStudent, action_params: dict[str, Any], msg: Message, state: FSMContext
) -> None:
    params = {}
    for param_name in action.get_required_params():
        params[param_name] = student

    params.update(action_params)

    action_result = action.run_action(**params)
    await state.set_state(BaseStates.main)
    await msg.answer(text=action_result, reply_markup=back_to_menu_kb)


async def _render_set_param(
    *,
    action: Action,
    action_id: str,
    param_index: int,
    msg: Message,
    state: FSMContext,
) -> None:
    current_param = list(action.get_params().items())[param_index]

    await state.set_state(ActionState.set_params)

    await state.update_data({"current_param_name": current_param[0]})
    await state.update_data({"action_id": action_id})
    await state.update_data({"params": {}})

    await msg.edit_text(text=f"Введите {current_param[1].display_name}:")


@main_router.callback_query(F.data.startswith("a."))
async def action_start(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)
    student = await _get_student_from_state(msg.chat.id, state)
    inst = await _get_inst_from_state(msg, state)

    if query.data is None:
        return

    action_id = query.data.split(".")[1]
    action = inst.action_container.get_action(action_id)

    if action is None:
        await query.answer("Такого действия не существует!")
        return

    if action.get_params():
        await _render_set_param(
            action=action,
            action_id=action_id,
            param_index=0,
            msg=msg,
            state=state,
        )
        return
    await _render_action_result(action, student, {}, msg, state)


@main_router.message(ActionState.set_params)
async def set_action_param(msg: Message, state: FSMContext) -> None:
    current_param_name = await state.get_value("current_param_name")
    action_id = await state.get_value("action_id")

    if not (current_param_name and action_id):
        return

    action = await _get_acion_from_state(action_id, msg, state)

    if not action:
        return

    current_param_type = action.get_params()[current_param_name]

    match current_param_type:
        case TextParam():
            params = await state.get_value("params", {})
            params.update({current_param_name: msg.text})

            await state.update_data({"params": params})

    if len(params) == len(action.get_params()):
        await _render_action_result(
            action,
            await _get_student_from_state(msg.chat.id, state),
            params,
            msg,
            state,
        )
        return

    current_param_index = list(action.get_params().keys()).index(
        current_param_name
    )
    await _render_set_param(
        action=action,
        action_id=action_id,
        param_index=current_param_index + 1,
        msg=msg,
        state=state,
    )


@main_router.callback_query()
async def process_menu_button(query: CallbackQuery, state: FSMContext) -> None:
    inst_raw = await state.get_value("inst")

    msg = _get_msg(query)

    if not isinstance(inst_raw, str):
        await msg.answer("у вас не выбрано учебное заведение. Введите /start!")
        return

    inst = institutions[InstitutionNames(inst_raw)]
    student = await _get_student_from_state(msg.chat.id, state)

    match query.data:
        case "today":
            today = await inst.schedule_getter.get_day_schedule_for(
                student, get_today()
            )

            await _edit_msg_to_action(format_schedule(today), msg)
        case "tommorow":
            today = await inst.schedule_getter.get_day_schedule_for(
                student, get_tommorow(get_today())
            )

            await _edit_msg_to_action(format_schedule(today), msg)

        case "remain_week":
            remain_week = await inst.schedule_getter.get_week_schedule_for(
                student, get_today()
            )

            await _edit_msg_to_action(
                format_schedule_for_week(remain_week), msg
            )

        case "next_week":
            next_week = await inst.schedule_getter.get_week_schedule_for(
                student, find_next_monday(get_today())
            )

            await _edit_msg_to_action(format_schedule_for_week(next_week), msg)
        case _:
            await _edit_msg_to_action("Что-то не то...\nПопробуйте /start", msg)
