from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

def create_country_keyboard(legue_list, callback: CallbackData):
    country_keyboard = InlineKeyboardMarkup(row_width=1)
    for legue in legue_list:
        country_keyboard.insert(InlineKeyboardButton(
            text = str(legue), 
            callback_data=callback.new(legue_name=legue.get_name())
        ))
    country_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"), 
        callback_data=callback.new(legue_name="cancel")
    ))
    return country_keyboard

def create_country_back_keyboard(callback: CallbackData):
    country_back_keyboard = InlineKeyboardMarkup()
    country_back_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(legue_name="back_to_list")
    ))
    return country_back_keyboard