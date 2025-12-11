from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.abstractions import InstitutionNames
from src.telegram.registration.sibadi_registration import (
    process_sibadi_registration,
)

router = Router()


registration_by_institution = {
    InstitutionNames.SIBADI: process_sibadi_registration
}


class CommonRegistrationState(StatesGroup):
    choose_institution = State()


def build_choose_institution_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for name in InstitutionNames:
        builder.button(text=name, callback_data=f"{name.value}")
    return builder.as_markup()


async def start_registration_process(
    message: Message, state: FSMContext
) -> None:
    await message.answer(
        text="Выберите ваше учебное заведение: ",
        reply_markup=build_choose_institution_keyboard(),
    )
    await state.set_state(CommonRegistrationState.choose_institution)


@router.callback_query(CommonRegistrationState.choose_institution)
async def test(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"inst": query.data})

    if not isinstance(query.data, str):
        return

    await registration_by_institution[InstitutionNames(query.data)](
        query, state
    )
