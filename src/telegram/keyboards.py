from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

back_to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="menu")]]
)
