from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager


def create_country_keyboard(callback: CallbackData):
    country_keyboard = InlineKeyboardMarkup(row_width=1)
    xbet = XBet()
    cm = CoeffManager(xbet)
    for league in cm.get_leagues():
        country_keyboard.insert(InlineKeyboardButton(
            text=str(cm.emojize_league(league) + ' ' + cm.translate_league(league)),
            callback_data=callback.new(legue_name=league)
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
