from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from keyboards.inline.callback_datas import menu_callback
from loader import user_manager


def create_menu_keyboard(tg_id):
    menu_keyboard = InlineKeyboardMarkup(row_width=1)
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F4CA Коэффициенты"), 
        callback_data=menu_callback.new(choice_name="coeffs")
    ))
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F51D Популярные игроки"), 
        callback_data=menu_callback.new(choice_name="players")
    ))
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F3AF Лучшие игроки"), 
        callback_data=menu_callback.new(choice_name="top")
    ))
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F4DA Источники"), 
        callback_data=menu_callback.new(choice_name="sources")
    ))
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F3AE Привязать профиль"), 
        callback_data=menu_callback.new(choice_name="profile")
    ))
    menu_keyboard.insert(InlineKeyboardButton(
        text=emojize("\U0001F527 Помощь"), 
        callback_data=menu_callback.new(choice_name="help")
    ))
    if user_manager.is_admin(tg_id):
        menu_keyboard.insert(InlineKeyboardButton(
            text=emojize("Админка"), 
            callback_data=menu_callback.new(choice_name="admin")
        ))
    return menu_keyboard


back_to_menu_keyboard = InlineKeyboardMarkup()
back_to_menu_keyboard.insert(InlineKeyboardButton(
    text=emojize(":leftwards_arrow_with_hook: Назад"),
    callback_data=menu_callback.new(choice_name="back_to_menu")
))
