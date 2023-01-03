from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from src.loader import dp
from src.manager_loader import coeff_manager
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, coeffs_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.coeff_buttons import (
    create_coeff_leagues_keyboard,
    create_coeff_back_keyboard,
)


@dp.callback_query_handler(
    coeffs_callback.filter(
        league_name="cancel",
    )
)
async def to_menu_from_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        text="Меню: ", reply_markup=create_menu_keyboard(call.from_user.id)
    )


@dp.callback_query_handler(
    coeffs_callback.filter(
        league_name="back_to_list",
    )
)
async def back_to_leagues_from_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        "Доступные чемпионаты:",
        reply_markup=create_coeff_leagues_keyboard(coeffs_callback),
    )


@dp.callback_query_handler(coeffs_callback.filter())
async def get_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        text=coeff_manager.get_coeffs(
            callback_data["league_name"], cur_round=(callback_data["round"] == "cur")
        ),
        reply_markup=create_coeff_back_keyboard(
            coeffs_callback,
            callback_data["league_name"],
            callback_data["round"] == "cur",
        ),
        parse_mode=ParseMode.HTML,
    )
