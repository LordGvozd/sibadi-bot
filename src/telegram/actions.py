from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.actions import (
    Action,
    Param,
    RenderData,
    SettingParams,
)
from src.institutions.types import AnyStudent
from src.telegram.getters import (
    get_action_from_state,
    get_current_param_from_state,
    get_inst_from_state,
    get_student_from_state,
)
from src.telegram.keyboards import back_to_menu_kb
from src.telegram.states import BaseStates

# Consts
actions_router = Router()


def setup_actions(base_router: Router) -> None:
    base_router.include_router(actions_router)


# Actions
class ActionState(StatesGroup):
    set_params = State()


# Utils
def _get_msg(query: CallbackQuery) -> Message:
    if isinstance(query.message, Message):
        return query.message
    raise Exception("Some error with query!")


async def _verify_param(
    current_param_type: Param, user_input: str, msg: Message
) -> bool:
    verify_result = await current_param_type.verify(user_input)

    if verify_result["verifcation_completed"]:
        return True
    await msg.answer(verify_result["msg"])
    return False



async def _set_action_param(
    user_input: str, msg: Message, state: FSMContext
) -> None:
    action = await get_action_from_state(msg, state)
    action_id = await state.get_value("action_id")

    if not (action and action_id):
        return

    current_param_name, current_param_type = await get_current_param_from_state(
        msg, state
    )

    params = await state.get_value("params", {})
    if not await _verify_param(current_param_type, user_input, msg):
        return

    if isinstance(current_param_type, SettingParams):
        data = await state.get_data()

        data[current_param_type.setting_name] = user_input
        await state.set_data(data)
    else:
        params[current_param_name] = user_input

        await state.update_data(params=params)

    # Go to next param
    current_param_index = list(action.get_params().keys()).index(
        current_param_name
    )
    if current_param_index + 1 == len(action.get_params()):
        await render_action_result(
            action,
            await get_student_from_state(msg.chat.id, state),
            params,
            msg,
            state,
        )
        return

    await _render_param_request(
        action=action,
        action_id=action_id,
        param_index=current_param_index + 1,
        msg=msg,
        state=state,
    )


# Render
async def render_action_result(
    action: Action,
    student: AnyStudent,
    action_params: dict[str, Any],
    msg: Message,
    state: FSMContext,
) -> None:
    params = {}
    for param_name in action.get_required_params():
        params[param_name] = student

    params.update(action_params)

    action_result = action.run_action(**params)

    await state.set_state(BaseStates.main)
    await state.update_data(params=None)

    await msg.answer(text=action_result, reply_markup=back_to_menu_kb)


def _build_kb_from_render_data(
    render_data: RenderData,
) -> InlineKeyboardMarkup | None:
    if render_data["reply_markup"] is None:
        return None

    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    
    for index, button in enumerate(render_data["reply_markup"]):
        builder.button(text=button, callback_data=str(index))

    return builder.as_markup()


async def _render_param_request(
    *,
    action: Action,
    action_id: str,
    param_index: int,
    msg: Message,
    state: FSMContext,
) -> None:
    """Send message, that request param. """
    current_param_id, current_param = list(action.get_params().items())[
        param_index
    ]
    
    # If already know param
    if isinstance(current_param, SettingParams):
        value_from_state = await state.get_value(current_param.setting_name)

        if value_from_state is not None:
            current_param_index = list(action.get_params().keys()).index(
                current_param_id
            )
            if current_param_index + 1 == len(action.get_params()):
                params = await state.get_value("params", dict())
                await render_action_result(
                    action,
                    await get_student_from_state(msg.chat.id, state),
                    params,
                    msg,
                    state,
                )
                return

            await _render_param_request(
                action=action,
                action_id=action_id,
                param_index=current_param_index + 1,
                msg=msg,
                state=state,
            )
            return 


    await state.set_state(ActionState.set_params)

    await state.update_data({"current_param_name": current_param_id})
    await state.update_data({"action_id": action_id})

    render_data = await current_param.get_render_data()

    kb = _build_kb_from_render_data(render_data)

    if msg.from_user and msg.from_user.is_bot:
        await msg.edit_text(text=render_data["text"], reply_markup=kb)
    else:
        await msg.answer(text=render_data["text"], reply_markup=kb)


# Bindings to router
@actions_router.callback_query(F.data == "action")
async def open_action_menu(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    inst = await get_inst_from_state(msg, state)

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


@actions_router.callback_query(F.data.startswith("a."))
async def action_start(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)
    student = await get_student_from_state(msg.chat.id, state)
    inst = await get_inst_from_state(msg, state)

    if query.data is None:
        return

    action_id = query.data.split(".")[1]
    action = inst.action_container.get_action(action_id)

    if action is None:
        await query.answer("Такого действия не существует!")
        return

    if action.get_params():
        await _render_param_request(
            action=action,
            action_id=action_id,
            param_index=0,
            msg=msg,
            state=state,
        )
        return
    await render_action_result(action, student, {}, msg, state)


@actions_router.message(ActionState.set_params)
async def set_param_text_based(msg: Message, state: FSMContext) -> None:
    if not msg.text:
        await msg.answer("Пожалуйста, отправь текст и мне пиво!")
        return
    await _set_action_param(msg.text, msg, state)


@actions_router.callback_query(ActionState.set_params)
async def set_param_query_based(
    query: CallbackQuery, state: FSMContext
) -> None:
    msg = _get_msg(query)

    query_data = query.data

    if query_data is None:
        await query.answer("Something wrong!")
        return

    keyboard = msg.reply_markup

    if not keyboard:
        await query.answer("Something wrong!")
        return

    button_index = int(query_data)

    buttons = []
    for row in keyboard.inline_keyboard:
        buttons.extend(button.text for button in row)

    user_input = buttons[button_index]

    await _set_action_param(user_input, msg, state)
