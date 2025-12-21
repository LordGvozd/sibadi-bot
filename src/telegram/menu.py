from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.formaters import (
    format_schedule,
    format_schedule_for_week,
    format_timetable,
)
from src.telegram.getters import (
    get_inst_from_state,
    get_student_from_state,
)
from src.telegram.keyboards import back_to_menu_kb
from src.telegram.states import BaseStates
from src.telegram.time_utils import find_next_monday, get_today, get_tommorow

main_router = Router()


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


def _get_msg(query: CallbackQuery) -> Message:
    if isinstance(query.message, Message):
        return query.message
    raise Exception("Some error with query!")


@main_router.callback_query(F.data == "menu")
async def proceess_menu(query: CallbackQuery, state: FSMContext) -> None:
    await open_menu(_get_msg(query), state)


@main_router.callback_query(F.data == "today")
async def proceess_today(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    student = await get_student_from_state(msg.chat.id, state)
    inst = await get_inst_from_state(msg, state)

    today = await inst.schedule_getter.get_day_schedule_for(
        student, get_today()
    )

    await _edit_msg_to_action(format_schedule(today), msg)


@main_router.callback_query(F.data == "tommorow")
async def proceess_tommorow(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    student = await get_student_from_state(msg.chat.id, state)
    inst = await get_inst_from_state(msg, state)

    tommorow = await inst.schedule_getter.get_day_schedule_for(
        student, get_tommorow(get_today())
    )

    await _edit_msg_to_action(format_schedule(tommorow), msg)


@main_router.callback_query(F.data == "remain_week")
async def process_remain_week(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    student = await get_student_from_state(msg.chat.id, state)
    inst = await get_inst_from_state(msg, state)
    remain_week = await inst.schedule_getter.get_week_schedule_for(
        student, get_today()
    )

    await _edit_msg_to_action(format_schedule_for_week(remain_week), msg)


@main_router.callback_query(F.data == "next_week")
async def process_next_week(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    student = await get_student_from_state(msg.chat.id, state)
    inst = await get_inst_from_state(msg, state)
    next_week = await inst.schedule_getter.get_week_schedule_for(
        student, find_next_monday(get_today())
    )

    await _edit_msg_to_action(format_schedule_for_week(next_week), msg)

@main_router.callback_query(F.data == "time")
async def proccess_time(query: CallbackQuery, state: FSMContext) -> None:
    msg = _get_msg(query)

    inst = await get_inst_from_state(msg, state)

    await _edit_msg_to_action(format_timetable(inst.get_timetable), msg)


@main_router.callback_query()
async def process_unknow_query(query: CallbackQuery) -> None:
    msg = _get_msg(query)
    await _edit_msg_to_action("Что-то не то...\nПопробуйте /start", msg)
