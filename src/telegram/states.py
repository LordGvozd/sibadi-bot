from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    menu = State()
    time = State()
    today = State()
    tommorow = State()
    remain_week = State()
    next_week = State()
