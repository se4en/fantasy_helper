from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from loader import Users
from states.menu import Menu
from keyboards.inline.menu_buttons import choice

from keyboards.inline.callback_datas import menu_callback
from keyboards.inline.coefs_buttons import create_coefs_keyboard
from aiogram.types import CallbackQuery

@dp.message_handler(CommandStart(), state=None)
async def bot_start(message: types.Message):
    if Users.get_profile(message.from_user.id):
        await Menu.main_menu.set()
        await message.answer(text=f"Привет, {message.from_user.full_name}!",
                             reply_markup=choice)
    else:
        text = [
            f"Привет, {message.from_user.full_name}!",
            "Отправь мне ссылку на свой профиль на sports.ru"
        ]
        await message.answer('\n'.join(text))
        await Menu.get_profile_url.set()


@dp.callback_query_handler(menu_callback.filter())
async def to_coefs(call: CallbackQuery, callback_data: dict):
    print("here")
    await call.answer(cache_time=60)
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_coefs_keyboard())