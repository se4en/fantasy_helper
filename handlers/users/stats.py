from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from keyboards.inline.stats_buttons import create_stats_leagues_keyboard, create_stats_league_back_keyboard, \
    create_stats_league_menu_keyboard
from loader import dp, player_stats_manager
from states.checking import Check
from keyboards.inline.callback_datas import stats_callback
from keyboards.inline.menu_buttons import create_menu_keyboard


@dp.callback_query_handler(stats_callback.filter(league_name="cancel", ),
                           state=Check.no_checking)
async def to_menu_from_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ",
                              reply_markup=create_menu_keyboard(call.message.from_user.id))


@dp.callback_query_handler(stats_callback.filter(league_name="back_to_list", ),
                           state=Check.no_checking)
async def back_to_leagues_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_stats_leagues_keyboard(stats_callback),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(stats_callback.filter(type="shoots"), state=Check.no_checking)
async def get_shoots_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text=player_stats_manager.get_players_shoots(callback_data["league_name"],
                                                                           callback_data["last_5"] == "True"),
                              reply_markup=create_stats_league_back_keyboard(stats_callback,
                                                                             callback_data["league_name"]),
                              parse_mode=ParseMode.HTML)


# must be last handler
@dp.callback_query_handler(stats_callback.filter(), state=Check.no_checking)
async def get_league_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Доступная статистика:",
                              reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                             callback_data["league_name"]),
                              parse_mode=ParseMode.MARKDOWN)
