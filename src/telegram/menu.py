from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.abstractions import InstitutionNames, Student
from src.formaters import (
    format_schedule,
    format_schedule_for_week,
    format_timetable,
)
from src.institutions.sibadi.sibadi import Sibadi, SibadiStudent
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

    await state.set_state(BaseStates.main)
    await msg.edit_text(
        text="Привет! Это меню.", reply_markup=builder.as_markup()
    )


async def _edit_msg_to_action(text: str, msg: Message) -> None:
    await msg.edit_text(text=text, reply_markup=back_to_menu_kb)


async def _get_student_from_state(tg_id: int, state: FSMContext) -> Student:
    match InstitutionNames(await state.get_value("inst")):
        case InstitutionNames.SIBADI:
            group_id = await state.get_value("group_id")

            if not group_id:
                raise ValueError

            return SibadiStudent(tg_id=str(tg_id), group_id=group_id)


@main_router.callback_query(CallbackData.filter("menu"))
@main_router.callback_query()
async def process_menu_button(query: CallbackQuery, state: FSMContext) -> None:
    inst_raw = await state.get_value("inst")
    if not isinstance(query.message, Message):
        return
    if inst_raw is None:
        await query.message.answer(
            "у вас не выбрано учебное заведение. Введите /start!"
        )

    inst = institutions[InstitutionNames(inst_raw)]
    student = await _get_student_from_state(query.message.chat.id, state)

    match query.data:
        case "menu":
            await open_menu(query.message, state)
        case "time":
            timetable = inst.get_timetable

            await _edit_msg_to_action(
                format_timetable(timetable), query.message
            )
        case "today":
            today = await inst.schedule_getter.get_day_schedule_for(
                student, get_today()
            )

            await _edit_msg_to_action(format_schedule(today), query.message)
        case "tommorow":
            today = await inst.schedule_getter.get_day_schedule_for(
                student, get_tommorow(get_today())
            )

            await _edit_msg_to_action(format_schedule(today), query.message)

        case "remain_week":
            remain_week = await inst.schedule_getter.get_week_schedule_for(
                student, get_today()
            )

            await _edit_msg_to_action(
                format_schedule_for_week(remain_week), query.message
            )

        case "next_week":
            next_week = await inst.schedule_getter.get_week_schedule_for(
                student, find_next_monday(get_today())
            )

            await _edit_msg_to_action(
                format_schedule_for_week(next_week), query.message
            )
        case _:
            await _edit_msg_to_action("Что-то не то...", query.message)
