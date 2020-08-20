from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from loader import Users
from states.menu import Menu
from keyboards.inline.menu_buttons import menu_keyboard

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=menu_keyboard)