from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Back, Button, Column, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.telegram.logic import next_week_getter, remain_week_getter, today_schedule_gettter
from src.telegram.states import BotState

back = SwitchTo(Const("Меню"), "menu", state=BotState.menu)

menu_window = Window(
    Const("Привет! Это меню."),
    Column(
        SwitchTo(Const("Звонки"), id="time", state=BotState.time),
        SwitchTo(Const("Сегодня"), id="today", state=BotState.today),
        SwitchTo(Const("Текущяя неделя"), id="remain_week", state=BotState.remain_week),
        SwitchTo(Const("Следущяя неделя"), id="next_week", state=BotState.next_week),
    ),

    state=BotState.menu,
)

time_window = Window(
    Const("""
1) 8:20 - 9:50
2) 10:00 - 11:30
3) 11:40 - 13:10
4) 13:45 - 15:15
5) 15:25 - 16:55
6) 17:05 - 18:35
    """),
    back,
    state=BotState.time
)

today_window = Window(
    Format("{schedule}"),
    back,
    getter=today_schedule_gettter,
    state=BotState.today
)

remain_week_window = Window(
    Format("{schedule}"),
    back,
    getter=remain_week_getter,
    state=BotState.remain_week
)

next_week_window = Window(
    Format("{schedule}"),
    back,
    getter=next_week_getter,
    state=BotState.next_week
)



main_dialog = Dialog(
    menu_window,
    time_window,
    today_window,
    remain_week_window,
    next_week_window,
)


