from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager
from keyboards.inline.callback_datas import sources_callback


def create_sources_keyboard():
    sources_keyboard = InlineKeyboardMarkup(row_width=1)
    # TODO change to leagues info
    xbet = XBet()
    cm = CoeffManager(xbet)
    leagues = cm.get_leagues()
    for league in leagues:
        sources_keyboard.insert(InlineKeyboardButton(
            text=str(cm.emojize_league(league) + ' ' + cm.translate_league(league)),
            callback_data=sources_callback.new(league_name=league)
        ))
    sources_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"), 
        callback_data=sources_callback.new(league_name="cancel")
    ))  
    return sources_keyboard


sources_back_keyboard = InlineKeyboardMarkup()
sources_back_keyboard.insert(InlineKeyboardButton(
    text=emojize(":leftwards_arrow_with_hook: Назад"),
    callback_data=sources_callback.new(league_name="back_to_list")
))
