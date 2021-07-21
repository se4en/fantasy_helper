from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager


def create_coeff_keyboard(callback: CallbackData):
    country_keyboard = InlineKeyboardMarkup(row_width=1)
    xbet = XBet()
    cm = CoeffManager(xbet)
    for league in cm.get_leagues():
        country_keyboard.insert(InlineKeyboardButton(
            text=str(cm.emojize_league(league) + ' ' + cm.translate_league(league)),
            callback_data=callback.new(league_name=league, round="cur")
        ))
    country_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"), 
        callback_data=callback.new(league_name="cancel", round="cur")
    ))
    return country_keyboard


def create_coeff_back_keyboard(callback: CallbackData, league_name: str, cur_round: bool):
    coeff_back_keyboard = InlineKeyboardMarkup(row_width=2)
    coeff_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(league_name="back_to_list", round="cur")
    )
    if cur_round:
        coeff_round_button = InlineKeyboardButton(
            text=emojize("➡️ Cледующий тур"),
            callback_data=callback.new(league_name=league_name, round="next")
        )
    else:
        coeff_round_button = InlineKeyboardButton(
            text=emojize("⬅️ Текущий тур"),
            callback_data=callback.new(league_name=league_name, round="cur")
        )
    coeff_back_keyboard.add(coeff_back_button, coeff_round_button)
    return coeff_back_keyboard
