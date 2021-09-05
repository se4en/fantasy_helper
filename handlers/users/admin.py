from aiogram import types
from aiogram.types import CallbackQuery

from data import config
from loader import dp
from states.checking import Check
from keyboards.inline.callback_datas import admin_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.admin_buttons import create_leagues_keyboard, create_admin_keyboard
from keyboards.inline.sources_buttons import create_sources_keyboard
from utils.updates import update_players, update_coeffs, update_players_stats, update_all


@dp.callback_query_handler(admin_callback.filter(tool_name=["update_players", "update_coeffs", "update_stats"],
                                                 league_name="None"),
                           state=Check.no_checking)
async def get_update_players_leagues(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Выберите чемпионат: ",
                              reply_markup=create_leagues_keyboard(callback_data['tool_name']))


@dp.callback_query_handler(admin_callback.filter(tool_name=["update_players", "update_coeffs", "update_stats",
                                                            "update_all"], ))
async def admin_update_resource(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    if callback_data["tool_name"] == "update_players":
        update_players(callback_data["league_name"], new_round=False)
    elif callback_data["tool_name"] == "update_coeffs":
        await update_coeffs(callback_data["league_name"])
    elif callback_data["tool_name"] == "update_stats":
        await update_players_stats(callback_data["league_name"], new_round=False)
    elif callback_data["tool_name"] == "update_all":
        await update_all()
    await call.message.answer(text="Доступные инструменты:", reply_markup=create_admin_keyboard())


@dp.callback_query_handler(admin_callback.filter(tool_name="add_source", ))
async def admin_manage_source_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Выберите чемпионат:", reply_markup=create_sources_keyboard("add"))


@dp.callback_query_handler(admin_callback.filter(tool_name="delete_source", ))
async def admin_manage_source_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Выберите чемпионат:", reply_markup=create_sources_keyboard("delete"))


@dp.callback_query_handler(admin_callback.filter(tool_name="back_to_list", ))
async def back_to_admin_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Доступные инструменты:", reply_markup=create_admin_keyboard())


@dp.callback_query_handler(admin_callback.filter(tool_name="cancel", ))
async def to_menu_from_admin(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ",
                              reply_markup=create_menu_keyboard(call.from_user.id))
