from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from data import config
from loader import dp
from states.checking import Check
from keyboards.inline.menu_buttons import create_menu_keyboard
from domain.users import UserManager


@dp.message_handler(state=Check.checking_password)
async def bot_checking_password(message: types.Message):
    if message.text == config.PASSWORD:
        await Check.no_checking.set()
        um = UserManager()  # message.from_user.username
        um.make_valid(message.from_user.id)
        await message.answer(text="Меню:", reply_markup=create_menu_keyboard(message.from_user.id))
    else:
        await message.answer(text="Пароль неверный!\nПовторите попытку:")


@dp.message_handler(state=Check.getting_profile)
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    um = UserManager()
    um.add_profile(message.from_user.id, message.text)
    await message.answer(text="Меню:", reply_markup=create_menu_keyboard(message.from_user.id))
