from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from dotenv import load_dotenv

from src.config import settings
from src.telegram.states import BotState
from src.telegram.windows import main_dialog

load_dotenv()

bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(main_dialog)


@dp.message(CommandStart())
async def start(message: types.Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(BotState.menu, mode=StartMode.RESET_STACK)


async def run_bot() -> None:
    """Запуск бота."""
    setup_dialogs(dp)
    await dp.start_polling(bot)
