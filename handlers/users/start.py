from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from loader import users
from states.checking import Check
from keyboards.inline.menu_buttons import create_menu_keyboard

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if users.check_password(message.from_user.id):
        await Check.no_checking.set()
        await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=create_menu_keyboard(message.from_user.id))
    else:
        await Check.checking_password.set()
        answer = [f"Привет, {message.from_user.full_name}!",
                 "Введите пароль:"]
        await message.answer(text=("\n").join(answer))

@dp.message_handler(CommandStart(), state=Check.no_checking)
async def bot_start_after_login(message: types.Message):
    await Check.no_checking.set()
    await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=create_menu_keyboard(message.from_user.id))