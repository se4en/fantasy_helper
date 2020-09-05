from aiogram import types

from data import config
from loader import dp
from loader import users
from states.checking import Check
from keyboards.inline.menu_buttons import create_menu_keyboard

@dp.message_handler(state=Check.checking_password)
async def bot_checking_password(message: types.Message):
    if message.text==config.PASSWORD:
        await Check.no_checking.set()
        users.add_user(message.from_user.id)
        await message.answer(text="Меню:", reply_markup=create_menu_keyboard(0))
    else:
        await message.answer(text="Пароль неверный!\nПовторите попытку:")

@dp.message_handler(state=Check.getting_profile)
async def bot_start(message: types.Message):
    await Check.no_checking.set()
    users.add_profile(message.from_user.id, message.text)
    await message.answer(text="Меню:", reply_markup=create_menu_keyboard(0))