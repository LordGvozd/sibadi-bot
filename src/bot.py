from datetime import datetime
from os import environ
from functools import lru_cache
import calendar

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart, Command
from dotenv import load_dotenv

from src.models import Schedule, Lesson
from src.parser import get_day_schedule, get_remain_week_schedule

load_dotenv()

bot = Bot(
    token=environ["token"],
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()

@lru_cache()
def _format_schedule(schedule: Schedule) -> str:
    head = f"распорядок на: <i>{schedule.date.strftime('%d-%m-%Y')}</i>\n\n"

    body = "\n".join([
        f"{lesson.number}) <i>[{lesson.starts_at.strftime('%H:%M')}]</i> <b>{lesson.name.title()}</b> <code>{lesson.audience}</code>"
        for lesson in schedule.lessons
    ])

    return head + body

@lru_cache()
def _get_days_in_month(date: datetime) -> int:
    month_number = date.month
    year_number = date.year

    return calendar.monthrange(year_number, month_number)[1]

@lru_cache()
def _find_next_monday(date: datetime) -> datetime:
    days_in_month = _get_days_in_month(date)

    to_next_monday = date.day + (6 - date.weekday())

    if to_next_monday > days_in_month:
        to_next_monday -= days_in_month

    monday = datetime(year=date.year, month=date.month, day=to_next_monday)

    return monday


async def _send_schedule_for_week(msg: types.Message, date: datetime) -> None:
    schedule_list = get_remain_week_schedule(date)

    if schedule_list:
        answer_text = "\n\n\n".join([
            _format_schedule(day) for day in schedule_list
        ])

        await msg.answer(answer_text)
        return
    await msg.answer("Похоже, вы свободны до конца недели :)")

def get_today() -> datetime:
    now = datetime.now()

    return now.replace(hour=0, minute=1, second=0, microsecond=1)


@dp.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    await msg.answer("""
Привет! Этот бот покажет распорядок для прикладной информатики :)

/today - узнать распорядок на сегодня
/week - узнать распорядок на неделю
/next_week - узнать распорядок на следущюю неделю
/time - узнать время занятий

P.S Функционал будет расширяться, если мне не будет лень.
    """)


@dp.message(Command("today"))
async def cmd_today(msg: types.Message) -> None:
    schedule = get_day_schedule(get_today())
    if schedule:
        await msg.answer(_format_schedule(schedule))
        return
    await msg.answer("Похоже, сегодня нет занятий")


@dp.message(Command("week"))
async def cmd_week(msg: types.Message) -> None:
    await _send_schedule_for_week(msg, datetime.now())


@dp.message(Command("next_week"))
async def cmd_next_week(msg: types.Message) -> None:
    today = get_today()
    next_monday = _find_next_monday(today)
    await _send_schedule_for_week(msg, next_monday)


@dp.message(Command("time"))
async def cmd_time(msg: types.Message) -> None:
    await msg.answer("""
1) 8:20 - 9:50
2) 10:00 - 11:30
3) 11:40 - 13:10
4) 13:45 - 15:15
5) 15:25 - 16:55
6) 17:05 - 18:35
    """)


@dp.message(Command("version"))
async def cmd_version(msg: types.Message) -> None:
    await msg.answer("0.0.1")


async def run_bot():
    """Запуск бота."""
    await dp.start_polling(bot)
