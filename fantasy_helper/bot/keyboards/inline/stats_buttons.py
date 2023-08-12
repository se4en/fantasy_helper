from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callback_datas import stats_callback
from fantasy_helper.manager_loader import player_stats_manager
from fantasy_helper.manager_loader import fbref


def create_stats_leagues_keyboard(callback: CallbackData):
    leagues_keyboard = InlineKeyboardMarkup(row_width=1)
    for league in fbref.shoots_leagues:
        leagues_keyboard.insert(
            InlineKeyboardButton(
                text=str(
                    player_stats_manager.emojize_league(league)
                    + " "
                    + player_stats_manager.translate_league(league)
                ),
                callback_data=stats_callback.new(
                    league_name=league, type="None", last_5=False
                ),
            )
        )
    leagues_keyboard.insert(
        InlineKeyboardButton(
            text=emojize(":leftwards_arrow_with_hook: Назад"),
            callback_data=stats_callback.new(
                league_name="cancel", type="None", last_5=False
            ),
        )
    )
    return leagues_keyboard


def create_stats_league_menu_keyboard(callback: CallbackData, league_name: str):
    league_menu_keyboard = InlineKeyboardMarkup(row_width=2)

    if league_name in fbref.shoots_leagues:
        last_3_shoots_button = InlineKeyboardButton(
            text=emojize("Удары по воротам (3 тура)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="shoots", last_5=False
            ),
        )
        league_menu_keyboard.add(last_3_shoots_button)
        last_5_shoots_button = InlineKeyboardButton(
            text=emojize("Удары по воротам (5 туров)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="shoots", last_5=True
            ),
        )
        league_menu_keyboard.add(last_5_shoots_button)

    if league_name in fbref.xg_leagues:
        last_3_xg_button = InlineKeyboardButton(
            text=emojize("XG (3 тура)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="xg", last_5=False
            ),
        )
        last_3_xg_xa_button = InlineKeyboardButton(
            text=emojize("XG+XA (3 тура)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="xg_xa", last_5=False
            ),
        )
        league_menu_keyboard.add(last_3_xg_button, last_3_xg_xa_button)

        last_5_xg_button = InlineKeyboardButton(
            text=emojize("XG (5 туров)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="xg", last_5=True
            ),
        )
        last_5_xg_xa_button = InlineKeyboardButton(
            text=emojize("XG+XA (5 туров)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="xg_xa", last_5=True
            ),
        )
        league_menu_keyboard.add(last_5_xg_button, last_5_xg_xa_button)

    if league_name in fbref.shoots_creation_leagues:
        last_3_sca_button = InlineKeyboardButton(
            text=emojize("SCA (3 тура)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="sca", last_5=False
            ),
        )
        last_3_gca_button = InlineKeyboardButton(
            text=emojize("GCA (3 тура)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="gca", last_5=False
            ),
        )
        league_menu_keyboard.add(last_3_sca_button, last_3_gca_button)

        last_5_sca_button = InlineKeyboardButton(
            text=emojize("SCA (5 туров)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="sca", last_5=True
            ),
        )
        last_5_gca_button = InlineKeyboardButton(
            text=emojize("GCA (5 туров)"),
            callback_data=stats_callback.new(
                league_name=league_name, type="gca", last_5=True
            ),
        )
        league_menu_keyboard.add(last_5_sca_button, last_5_gca_button)

    back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=stats_callback.new(
            league_name="back_to_list", type="None", last_5=False
        ),
    )
    league_menu_keyboard.add(back_button)

    return league_menu_keyboard


def create_stats_league_back_keyboard(callback: CallbackData, league_name: str):
    stats_back_keyboard = InlineKeyboardMarkup(row_width=1)
    stats_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=stats_callback.new(
            league_name=league_name, type="None", last_5=False
        ),
    )
    stats_back_keyboard.add(stats_back_button)
    return stats_back_keyboard
