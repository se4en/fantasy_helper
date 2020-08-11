from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from keyboards.inline.callback_datas import menu_callback

choice = InlineKeyboardMarkup(row_width=1)
choice.insert(InlineKeyboardButton(text="Коэффициенты", callback_data="menu:coefs"))
choice.insert(InlineKeyboardButton(text="Помощь", callback_data=menu_callback.new(choice_name="help")))
