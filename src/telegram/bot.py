from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from src.config import settings
from src.repo import AbstractStudentRepo, InMemoryRepo
from src.telegram.menu import main_router
from src.telegram.registration import router, start_registration_process

# from src.telegram.states import BotState, RegisterState
# from src.telegram.windows import main_dialog

load_dotenv()


repo = InMemoryRepo()

bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp["repo"] = repo

dp.include_router(router)
dp.include_router(main_router)


@dp.message(CommandStart())
async def start(
    message: types.Message, state: FSMContext, repo: AbstractStudentRepo
) -> None:
    await start_registration_process(message, state)


async def run_bot() -> None:
    """Запуск бота."""
    await dp.start_polling(bot)
