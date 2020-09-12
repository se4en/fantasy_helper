from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from loader import players
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, players_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.country_buttons import create_country_keyboard, create_country_back_keyboard

@dp.callback_query_handler(players_callback.filter(legue_name="cancel",), state=Check.no_checking)
async def to_menu_from_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(call.message.from_user.id))

@dp.callback_query_handler(players_callback.filter(legue_name="back_to_list",), state=Check.no_checking)
async def back_to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_country_keyboard(players, players_callback),
                              parse_mode=ParseMode.HTML)

@dp.callback_query_handler(players_callback.filter(), state=Check.no_checking)
async def get_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    legue_name = callback_data["legue_name"]
    for players_legue in players:
        if players_legue.get_name()==legue_name:
            await call.message.answer(text=players_legue.get_popular(),
                                      reply_markup=create_country_back_keyboard(players_callback),
                                      parse_mode=ParseMode.HTML)