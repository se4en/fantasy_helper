from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from fantasy_helper.loader import dp
from fantasy_helper.manager_loader import player_manager
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, players_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.player_buttons import (
    create_player_leagues_keyboard,
    create_player_back_keyboard,
)


@dp.callback_query_handler(
    players_callback.filter(
        league_name="cancel",
    )
)
async def to_menu_from_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        text="Меню: ", reply_markup=create_menu_keyboard(call.from_user.id)
    )


@dp.callback_query_handler(
    players_callback.filter(
        league_name="back_to_list",
    )
)
async def back_to_leafues_from_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        "Доступные чемпионаты:",
        reply_markup=create_player_leagues_keyboard(players_callback),
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.callback_query_handler(players_callback.filter())
async def get_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(
        text=player_manager.get_players(callback_data["league_name"]),
        reply_markup=create_player_back_keyboard(players_callback),
        parse_mode=ParseMode.MARKDOWN,
    )
