from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager
from keyboards.inline.callback_datas import sourses_callback


def create_sourses_keyboard():
    sourses_keyboard = InlineKeyboardMarkup(row_width=1)
    # TODO change to leagues info
    xbet = XBet()
    cm = CoeffManager(xbet)
    leagues = cm.get_leagues()
    for league in leagues:
        sourses_keyboard.insert(InlineKeyboardButton(
            text=str(cm.emojize_league(league) + ' ' + cm.translate_league(league)),
            callback_data=sourses_callback.new(legue_name=league)
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
