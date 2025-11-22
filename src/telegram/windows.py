from typing import Final

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Column, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.telegram.constants import SCHEDULE_KEY, TIME_INFO
from src.telegram.logic import (
    next_week_getter,
    remain_week_getter,
    today_schedule_gettter,
    tommorow_schedule_getter,
)
from src.telegram.states import BotState

SCHEDULE_FORMAT_STRING: Final[str] = f"{{{SCHEDULE_KEY}}}"
back = SwitchTo(Const("Меню"), "menu", state=BotState.menu)

menu_window = Window(
    Const("Привет! Это меню."),
    Column(
        SwitchTo(Const("Сегодня"), id="today", state=BotState.today),
        SwitchTo(Const("Завтра"), id="tommorow", state=BotState.tommorow),
        SwitchTo(
            Const("Текущяя неделя"),
            id="remain_week",
            state=BotState.remain_week,
        ),
        SwitchTo(
            Const("Следущяя неделя"), id="next_week", state=BotState.next_week
        ),
        SwitchTo(Const("Звонки"), id="time", state=BotState.time),
    ),
    state=BotState.menu,
)

time_window = Window(
    Const(TIME_INFO),
    back,
    state=BotState.time,
)

today_window = Window(
    Format(SCHEDULE_FORMAT_STRING),
    back,
    getter=today_schedule_gettter,
    state=BotState.today,
)

remain_week_window = Window(
    Format(SCHEDULE_FORMAT_STRING),
    back,
    getter=remain_week_getter,
    state=BotState.remain_week,
)

next_week_window = Window(
    Format(SCHEDULE_FORMAT_STRING),
    back,
    getter=next_week_getter,
    state=BotState.next_week,
)

tommorow_window = Window(
    Format(SCHEDULE_FORMAT_STRING),
    back,
    getter=tommorow_schedule_getter,
    state=BotState.tommorow,
)


main_dialog = Dialog(
    menu_window,
    time_window,
    today_window,
    tommorow_window,
    remain_week_window,
    next_week_window,
)
