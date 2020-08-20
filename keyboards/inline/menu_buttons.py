from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from keyboards.inline.callback_datas import menu_callback

menu_keyboard = InlineKeyboardMarkup(row_width=1)
menu_keyboard.insert(InlineKeyboardButton(
    text=emojize("Коэффициенты"), 
    callback_data=menu_callback.new(choice_name="coefs")
))
menu_keyboard.insert(InlineKeyboardButton(
    text=emojize("Привязать профиль"), 
    callback_data=menu_callback.new(choice_name="profile")
))
menu_keyboard.insert(InlineKeyboardButton(
    text=emojize("Помощь"), 
    callback_data=menu_callback.new(choice_name="help")
))

back_to_menu_keyboard = InlineKeyboardMarkup()
back_to_menu_keyboard.insert(InlineKeyboardButton(
    text=emojize(":leftwards_arrow_with_hook: Назад"),
    callback_data=menu_callback.new(choice_name="back_to_menu")
))