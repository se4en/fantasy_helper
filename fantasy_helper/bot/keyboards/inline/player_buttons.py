from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from fantasy_helper.manager_loader import coeff_manager


def create_player_leagues_keyboard(callback: CallbackData):
    leagues_keyboard = InlineKeyboardMarkup(row_width=1)
    for league in coeff_manager.get_leagues():
        leagues_keyboard.insert(
            InlineKeyboardButton(
                text=str(
                    coeff_manager.emojize_league(league)
                    + " "
                    + coeff_manager.translate_league(league)
                ),
                callback_data=callback.new(
                    league_name=league,
                ),
            )
        )
    leagues_keyboard.insert(
        InlineKeyboardButton(
            text=emojize(":leftwards_arrow_with_hook: Назад"),
            callback_data=callback.new(league_name="cancel"),
        )
    )
    return leagues_keyboard


def create_player_back_keyboard(callback: CallbackData):
    player_back_keyboard = InlineKeyboardMarkup(row_width=1)
    player_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(league_name="back_to_list"),
    )
    player_back_keyboard.add(player_back_button)
    return player_back_keyboard
