from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from keyboards.inline.callback_datas import sourses_callback
from loader import sourses

def create_sourses_keyboard():
    sourses_keyboard = InlineKeyboardMarkup(row_width=1)
    legues = sourses.get_legues()
    for legue, legue_name in legues:
        sourses_keyboard.insert(InlineKeyboardButton(
            text = legue_name,
            callback_data=sourses_callback.new(legue_name=legue)
        ))
    sourses_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"), 
        callback_data=sourses_callback.new(legue_name="cancel")
    ))  
    return sourses_keyboard

sourses_back_keyboard = InlineKeyboardMarkup()
sourses_back_keyboard.insert(InlineKeyboardButton(
    text=emojize(":leftwards_arrow_with_hook: Назад"),
    callback_data=sourses_callback.new(legue_name="back_to_list")
))