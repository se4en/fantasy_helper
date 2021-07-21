from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from db.parse.xbet import XBet
from domain.coeffs import CoeffManager
from loader import dp
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, coeffs_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.country_buttons import create_coeff_keyboard, create_coeff_back_keyboard


@dp.callback_query_handler(coeffs_callback.filter(league_name="cancel", ), state=Check.no_checking)
async def to_menu_from_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(call.message.from_user.id))


@dp.callback_query_handler(coeffs_callback.filter(league_name="back_to_list", ), state=Check.no_checking)
async def back_to_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_coeff_keyboard(coeffs_callback))


@dp.callback_query_handler(coeffs_callback.filter(), state=Check.no_checking)
async def get_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    league_name = callback_data["league_name"]
    cur_round: bool = callback_data["round"] == "cur"
    xbet = XBet()
    cm = CoeffManager(xbet)
    await call.message.answer(text=cm.get_coeffs(league_name, cur_round=cur_round),
                              reply_markup=create_coeff_back_keyboard(coeffs_callback,
                                                                      callback_data["league_name"],
                                                                      cur_round),
                              parse_mode=ParseMode.HTML)
