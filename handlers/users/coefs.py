from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager
from loader import dp
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, coefs_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.country_buttons import create_country_keyboard, create_country_back_keyboard


@dp.callback_query_handler(coefs_callback.filter(legue_name="cancel", ), state=Check.no_checking)
async def to_menu_from_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(call.message.from_user.id))


@dp.callback_query_handler(coefs_callback.filter(legue_name="back_to_list", ), state=Check.no_checking)
async def back_to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_country_keyboard(coefs_callback))


@dp.callback_query_handler(coefs_callback.filter(), state=Check.no_checking)
async def get_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    league_name = callback_data["legue_name"]
    xbet = XBet()
    cm = CoeffManager(xbet)
    await call.message.answer(text=cm.get_coeffs(league_name, cur_round=True),
                              reply_markup=create_country_back_keyboard(coefs_callback),
                              parse_mode=ParseMode.HTML)
