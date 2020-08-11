from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from keyboards.inline.callback_datas import coefs_callback
from loader import Legues

def create_coefs_keyboard():
    print("here")
    coefs = InlineKeyboardMarkup(row_width=1)
    for legue in Legues:
        coefs.insert(InlineKeyboardButton(text=str(legue), callback_data=coefs_callback.new(legue_name=legue.get_name())))
    coefs.insert(InlineKeyboardButton(text=emojize(":leftwards_arrow_with_hook: Назад"), callback_data=coefs_callback.new(legue_name="cancel")))
    return coefs