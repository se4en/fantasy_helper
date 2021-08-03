from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import admin_callback
from aiogram.utils.emoji import emojize
from manager_loader import coeff_manager


def create_admin_keyboard():
    admin_keyboard = InlineKeyboardMarkup(row_width=1)
    admin_keyboard.insert(InlineKeyboardButton(
        text="Обновить популярность",
        callback_data=admin_callback.new(tool_name="update_players", league_name="None")
    ))
    admin_keyboard.insert(InlineKeyboardButton(
        text="Обновить коэффициенты",
        callback_data=admin_callback.new(tool_name="update_coeffs", league_name="None")
    ))
    admin_keyboard.insert(InlineKeyboardButton(
        text="Обновить статистику",
        callback_data=admin_callback.new(tool_name="update_stats", league_name="None")
    ))
    admin_keyboard.insert(InlineKeyboardButton(
        text="Обновить все!",
        callback_data=admin_callback.new(tool_name="update_all", league_name="None")
    ))
    # admin_keyboard.insert(InlineKeyboardButton(
    #     text="Управление источниками",
    #     callback_data=admin_callback.new(tool_name="manage_source", league_name="None")
    # ))
    # admin_keyboard.insert(InlineKeyboardButton(
    #     text="Управление твиттером",
    #     callback_data=admin_callback.new(tool_name="manage_twitter", league_name="None")
    # ))
    admin_keyboard.insert(InlineKeyboardButton(
        text="Назад",
        callback_data=admin_callback.new(tool_name="cancel", league_name="None")
    ))
    return admin_keyboard


def create_leagues_keyboard(tool_name: str):
    leagues_keyboard = InlineKeyboardMarkup(row_width=1)
    for league in coeff_manager.get_leagues():
        leagues_keyboard.insert(InlineKeyboardButton(
            text=str(coeff_manager.emojize_league(league) + ' ' + coeff_manager.translate_league(league)),
            callback_data=admin_callback.new(tool_name=tool_name, league_name=league)
        ))
    leagues_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=admin_callback.new(tool_name="back_to_list", league_name="None")
    ))
    return leagues_keyboard
