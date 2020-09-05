from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from loader import legues
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, coefs_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.country_buttons import create_country_keyboard, create_country_back_keyboard

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(coefs_callback.filter(legue_name="cancel",))
async def to_menu_from_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(0))

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(coefs_callback.filter(legue_name="back_to_list",))
async def back_to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_country_keyboard(legues, coefs_callback), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(coefs_callback.filter())
async def get_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    legue_name = callback_data["legue_name"]
    for legue in legues:
        if legue.get_name()==legue_name:
            await call.message.answer(text=legue.get_coefs(), reply_markup=create_country_back_keyboard(coefs_callback), parse_mode=ParseMode.MARKDOWN)