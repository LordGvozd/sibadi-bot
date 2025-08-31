from datetime import datetime
from os import environ
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart, Command
from dotenv import load_dotenv

from src.models import Schedule, Lesson
from src.parser import get_day_schedule, get_remain_week_schedule

load_dotenv()

bot = Bot(token=environ["token"], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


def _format_schedule(schedule: Schedule) -> str:
    head = f"Расписание на: <i>{schedule.date.strftime('%d-%m-%Y')}</i>\n\n"

    body = "\n".join([
        f"{lesson.number}) <code>[{lesson.starts_at.strftime('%H:%M')}]</code> <b>{lesson.name.title()}</b> "
        for lesson in schedule.lessons
    ])

    return head + body


@dp.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    await msg.answer("""
Привет! Этот бот покажет расписание для прикладной информатики :)

/today - узнать расписание на сегодня
/week - узнать расписание на неделю

P.S Функционал будет расширяться, если мне не будет лень.
    """)


@dp.message(Command("today"))
async def cmd_today(msg: types.Message) -> None:
    schedule = get_day_schedule(datetime.now())
    if schedule:
        await msg.answer(_format_schedule(schedule))
        return
    await msg.answer("Похоже, сегодня нет занятий")

@dp.message(Command("week"))
async def cmd_week(msg: types.Message) -> None:
    schedule_list = get_remain_week_schedule(datetime.now())

    if schedule_list:
        answer_text = "\n\n\n".join([
            _format_schedule(day) for day in schedule_list
        ])

        await msg.answer(answer_text)
        return
    await msg.answer("Похоже, вы свободны до конца недели :)")

async def run_bot():
    """Запуск бота."""
    await dp.start_polling(bot)



