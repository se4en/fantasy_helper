from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize
from aiogram.utils.callback_data import CallbackData

from keyboards.inline.callback_datas import sources_callback
from manager_loader import coeff_manager


def create_sources_keyboard():
    sources_keyboard = InlineKeyboardMarkup(row_width=1)
    sources_keyboard.insert(InlineKeyboardButton(
        text=emojize(":globe_with_meridians: Все чемпионаты"),
        callback_data=sources_callback.new(league_name="all", action="None")
    ))
    leagues = coeff_manager.get_leagues()
    for league in leagues:
        sources_keyboard.insert(InlineKeyboardButton(
            text=str(coeff_manager.emojize_league(league) + ' ' + coeff_manager.translate_league(league)),
            callback_data=sources_callback.new(league_name=league, action="None")
        ))

    sources_keyboard.insert(InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=sources_callback.new(league_name="cancel",  action="None")
    ))
    return sources_keyboard


def create_sources_league_keyboard(callback: CallbackData, league_name: str):
    league_keyboard = InlineKeyboardMarkup(row_width=1)

    sources_add_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Добавить источник"),
        callback_data=callback.new(league_name=league_name, action="add"))
    league_keyboard.add(sources_add_button)

    sources_delete_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Удалить источник"),
        callback_data=callback.new(league_name=league_name, action="delete"))
    league_keyboard.add(sources_delete_button)

    sources_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(league_name="back_to_list", action="None"))
    league_keyboard.add(sources_back_button)

    return league_keyboard

# def create_sources_list_keyboard(action: str = "None"):
#     sources_keyboard = InlineKeyboardMarkup(row_width=1)
#     sources_keyboard.insert(InlineKeyboardButton(
#         text=emojize(":globe_with_meridians: Все чемпионаты"),
#         callback_data=sources_callback.new(league_name="all", name="None", url="None", action=action)
#     ))
#     leagues = coeff_manager.get_leagues()
#     for league in leagues:
#         sources_keyboard.insert(InlineKeyboardButton(
#             text=str(coeff_manager.emojize_league(league) + ' ' + coeff_manager.translate_league(league)),
#             callback_data=sources_callback.new(league_name=league, name="None", url="None", action=action)
#         ))
#     sources_keyboard.insert(InlineKeyboardButton(
#         text=emojize(":leftwards_arrow_with_hook: Назад"),
#         callback_data=sources_callback.new(league_name="cancel", name="None", url="None", action=action)
#     ))
#     return sources_keyboard


def create_sources_back_keyboard(callback: CallbackData):
    sources_back_keyboard = InlineKeyboardMarkup(row_width=1)
    sources_back_button = InlineKeyboardButton(
        text=emojize(":leftwards_arrow_with_hook: Назад"),
        callback_data=callback.new(league_name="back_to_list", name="None", url="None", action="None"))
    sources_back_keyboard.add(sources_back_button)
    return sources_back_keyboard
