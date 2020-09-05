from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.inline.callback_datas import admin_callback

admin_keyboard = InlineKeyboardMarkup(row_width=1)

admin_keyboard.insert(InlineKeyboardButton(
    text = "Добавить источник", 
    callback_data=admin_callback.new(tool_name="add_sourse")
))

admin_keyboard.insert(InlineKeyboardButton(
    text = "Удалить источник", 
    callback_data=admin_callback.new(tool_name="delete_sourse")
))      

admin_keyboard.insert(InlineKeyboardButton(
    text = "Назад", 
    callback_data=admin_callback.new(tool_name="cancel")
))  