from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from loader import legues, sourses
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, sourses_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.sourses_buttons import create_sourses_keyboard, sourses_back_keyboard

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(sourses_callback.filter(legue_name="cancel",))
async def to_menu_from_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(0))

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(sourses_callback.filter(legue_name="back_to_list",))
async def back_to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_sourses_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(sourses_callback.filter())
async def get_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text=sourses.get_sourses(callback_data["legue_name"]), reply_markup=sourses_back_keyboard, parse_mode=ParseMode.MARKDOWN)