from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery

from loader import dp
from states.menu import Menu
from loader import Users
from keyboards.inline.menu_buttons import choice
from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.coefs_buttons import create_coefs_keyboard

@dp.message_handler(state=Menu.get_profile_url)
async def bot_geturl(message: types.Message):
    Users.add_user(message.from_user.id, message.text)
    await Menu.main_menu.set()
    await message.answer(text="", reply_markup=choice)
    

@dp.callback_query_handler(menu_callback.filter())
async def to_coefs(call: CallbackQuery, callback_data: dict):
    print("here")
    await call.answer(cache_time=60)
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_coefs_keyboard())
#@dp.message_handler()