from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from fantasy_helper.manager_loader import coeff_manager


def create_coeff_leagues_keyboard(callback: CallbackData):
    country_keyboard = InlineKeyboardMarkup(row_width=1)
    for league in coeff_manager.get_leagues():
        country_keyboard.insert(
            InlineKeyboardButton(
                text=str(
                    coeff_manager.emojize_league(league)
                    + " "
                    + coeff_manager.translate_league(league)
                ),
                callback_data=callback.new(league_name=league, round="cur"),
            )
        )
    country_keyboard.insert(
        InlineKeyboardButton(
            text=emojize(":leftwards_arrow_with_hook: Назад"),
            callback_data=callback.new(league_name="cancel", round="cur"),
        )
    )
    return country_keyboard


def create_coeff_back_keyboard(
    callback: CallbackData, league_name: str, cur_round: bool
):
    coeff_back_keyboard = InlineKeyboardMarkup(row_width=2)
    coeff_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(league_name="back_to_list", round="cur"),
    )
    if cur_round:
        coeff_round_button = InlineKeyboardButton(
            text=emojize("➡️ Cледующий тур"),
            callback_data=callback.new(league_name=league_name, round="next"),
        )
    else:
        coeff_round_button = InlineKeyboardButton(
            text=emojize("⬅️ Текущий тур"),
            callback_data=callback.new(league_name=league_name, round="cur"),
        )
    coeff_back_keyboard.add(coeff_back_button, coeff_round_button)
    return coeff_back_keyboard
