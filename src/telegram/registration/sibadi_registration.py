from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from src.telegram.menu import back_to_menu_kb

from src.institutions.sibadi._parser import get_groups_dict

sibadi_router = Router()


class SibadiRegistrationState(StatesGroup):
    choose_group = State()


async def process_sibadi_registration(
    query: CallbackQuery, state: FSMContext
) -> None:
    if isinstance(query.message, Message):
        await query.message.edit_text(text="Введите название вашей группы")
        await state.set_state(SibadiRegistrationState.choose_group)


@sibadi_router.message(SibadiRegistrationState.choose_group)
async def choose_group(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Пожалуйста, отправте название группы!")
        return
    group_id = get_groups_dict().get(
        message.text.lower().replace("-", ""), None
    )

    if group_id is None:
        await message.answer("Такой группы нет!")
        return

    await state.update_data({"group_id": str(group_id)})
    await message.answer("Успешно!", reply_markup=back_to_menu_kb)
