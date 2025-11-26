from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.abstractions import InstitutionNames
from src.institutions.sibadi._parser import get_groups_dict
from src.telegram.menu import open_menu, back_to_menu_kb


router = Router()

class SibadiRegistrationState(StatesGroup):
    choose_group = State()

async def process_sibadi_registration(query: CallbackQuery, state: FSMContext) -> None: 
    await query.message.edit_text(text="Введите название вашей группы")
    await state.set_state(SibadiRegistrationState.choose_group)


registration_by_institution = {
    InstitutionNames.SIBADI: process_sibadi_registration
}

class CommonRegistrationState(StatesGroup):
    choose_institution = State()


def build_choose_institution_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for name in InstitutionNames:
        builder.button(text=name, callback_data=f"{name.value}")
    return  builder.as_markup()

async def start_registration_process(message: Message, state: FSMContext) -> None:
    await message.answer(text="Выберите ваше учебное заведение: ", 
                             reply_markup=build_choose_institution_keyboard(),
                         )
    await state.set_state(CommonRegistrationState.choose_institution)

async def end_regirstration_process(message: Message) -> None:
    await message.answer("Успешно!", reply_markup=back_to_menu_kb)



@router.callback_query(CommonRegistrationState.choose_institution)
async def test(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"inst": query.data})
    await registration_by_institution[InstitutionNames(query.data)](query, state)

@router.message(SibadiRegistrationState.choose_group)
async def choose_group(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Пожалуйста, отправте название группы!")
        return
    group_id = get_groups_dict().get(message.text.lower().replace("-", ""), None)

    if group_id is None:
        await message.answer("Такой группы нет!")
        return 

    await state.update_data({"group_id": str(group_id)})
    await end_regirstration_process(message)


