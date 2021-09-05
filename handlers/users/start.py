from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from datetime import datetime

from manager_loader import user_manager
from loader import dp
from db.models.user import User
from states.checking import Check
from keyboards.inline.menu_buttons import create_menu_keyboard


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_manager.add_user(message.from_user.id, message.from_user.username,
                          datetime.now(), valid=False)

    if user_manager.is_valid(message.from_user.id):
        await message.answer(text=f"Привет, {message.from_user.full_name}!",
                             reply_markup=create_menu_keyboard(message.from_user.id))
    else:
        await Check.checking_password.set()
        answer = [f"Привет, {message.from_user.full_name}!",
                  "Введите пароль:"]
        await message.answer(text="\n".join(answer))


@dp.message_handler(CommandStart())
async def bot_start_after_login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(text=f"Привет, {message.from_user.full_name}!",
                         reply_markup=create_menu_keyboard(message.from_user.id))
