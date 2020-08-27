from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from loader import users
from states.checking import Check
from keyboards.inline.menu_buttons import menu_keyboard

@dp.message_handler(state=Check.no_checking)
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if users.check_password(message.from_user.id):
        await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=menu_keyboard)
    else:
        await Check.checking_password.set()
        answer = [f"Привет, {message.from_user.full_name}!",
                 "Введите пароль:"]
        await message.answer(text=("\n").join(answer))