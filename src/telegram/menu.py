import asyncio
from collections.abc import Sequence
from typing import Any

import rapidfuzz
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
from src.actions import Action, ChoiceParam, Param, TextFromCollectionParam, TextParam
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
    msg: Message, state: FSMContext
) -> Action | None:
    action_id = await state.get_value("action_id")
    if action_id is None:
        return 

    inst = await _get_inst_from_state(msg, state)
    return inst.action_container.get_action(action_id)


async def _get_current_param_from_state(msg: Message, state: FSMContext) -> tuple[str, Param]:
    action = await _get_acion_from_state(msg, state)

    current_param_name = await state.get_value("current_param_name")
    if not current_param_name:
        raise Exception

    action = await _get_acion_from_state(msg, state)

    if not action:
        raise Exception

    current_param_type = action.get_params()[current_param_name]

    return str(current_param_name), current_param_type
    


async def _get_inst_from_state(msg: Message, state: FSMContext) -> Institution:
    inst_raw = await state.get_value("inst")

    if not isinstance(inst_raw, str):
        await msg.answer("у вас не выбрано учебное заведение. Введите /start!")
        raise Exception

    return institutions[InstitutionNames(inst_raw)]


async def _render_action_result(
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





async def _render_set_param(
    *,
    action: Action,
    action_id: str,
    param_index: int,
    msg: Message,
    state: FSMContext,
) -> None:
    current_param_id, current_param = list(action.get_params().items())[param_index]

    await state.set_state(ActionState.set_params)

    await state.update_data({"current_param_name": current_param_id})
    await state.update_data({"action_id": action_id})

    kb = None

    if isinstance(current_param, ChoiceParam):
        builder = InlineKeyboardBuilder()
        
        for index, variant in enumerate(current_param.variants):
            builder.button(text=variant.title(), callback_data=str(index))
        kb = builder.as_markup()
    
    if msg.from_user and msg.from_user.is_bot:
        await msg.edit_text(text=f"Введите {current_param.display_name}:", reply_markup=kb)
    else:
        await msg.answer(text=f"Введите {current_param.display_name}:", reply_markup=kb)


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


def _get_suggestions_sync(
    target: str, collection: Sequence[str], limit: int = 5
) -> list[str]:
    results = rapidfuzz.process.extract(
        target, collection, scorer=rapidfuzz.fuzz.WRatio, limit=limit
    )
    return [result[0] for result in results]


async def _get_suggestions_async(
    target: str, collection: Sequence[str], limit: int = 5
) -> list[str]:
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(
        None, _get_suggestions_sync, target, collection, limit
    )

async def _verify_param(current_param_type: Param, user_input: str, msg: Message) -> bool:
    match current_param_type:
        case TextParam():
            ...  # Just dont anythig, all text param will be valid
        case TextFromCollectionParam():
            # We must verify, that param value in collectoin, or get some suggestions
            if user_input not in current_param_type.collection:
                suggestoins = await _get_suggestions_async(
                    user_input, current_param_type.collection
                )
                answer_text = f"Неправильные данные! Возможно, вы имели ввиду {' или '.join(suggestoins)}?"

                await msg.answer(answer_text)
                return False
        case ChoiceParam():
            if user_input not in current_param_type.variants:
                await msg.answer("Ты что сделал чорт?")
                return False
    return True

@main_router.message(ActionState.set_params)
async def set_param_text_based(msg: Message, state: FSMContext) -> None:
    if not msg.text:
        await msg.answer("Пожалуйста, отправь текст и мне пиво!")
        return
    await _set_action_param(msg.text, msg, state)

@main_router.callback_query(ActionState.set_params)
async def set_param_query_based(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)
    
    _, current_param_type = await _get_current_param_from_state(msg, state)
    
    match current_param_type:
        case ChoiceParam():
            user_input = current_param_type.variants[int(query.data)]
        case _:
            raise Exception


    await _set_action_param(user_input, msg, state)


async def _set_action_param(user_input: str, msg: Message, state: FSMContext) -> None:
    action = await _get_acion_from_state(msg, state)
    action_id = await state.get_value("action_id")
    
    if not (action and action_id):
        return

    current_param_name, current_param_type = await _get_current_param_from_state(msg, state)

    if not await _verify_param(current_param_type, user_input, msg):
        return

    params = await state.get_value("params", dict())

    params[current_param_name] = user_input

    await state.update_data(params=params)
    

    
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
