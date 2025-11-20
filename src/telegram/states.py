from aiogram.fsm.state import StatesGroup, State


class BotState(StatesGroup):
    menu = State()
    time = State()
    today = State()
    remain_week = State()
    next_week = State()
