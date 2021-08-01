from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from keyboards.inline.player_buttons import create_player_leagues_keyboard
from loader import dp
from keyboards.inline.menu_buttons import create_menu_keyboard, back_to_menu_keyboard
from keyboards.inline.callback_datas import menu_callback, coeffs_callback, players_callback, stats_callback
from keyboards.inline.coeff_buttons import create_coeff_leagues_keyboard
from keyboards.inline.admin_buttons import create_admin_keyboard
from keyboards.inline.sources_buttons import create_sources_keyboard
from keyboards.inline.stats_buttons import create_stats_leagues_keyboard
from states.checking import Check


@dp.callback_query_handler(menu_callback.filter(choice_name="coeffs"), state=Check.no_checking)
async def to_coeffs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_coeff_leagues_keyboard(coeffs_callback),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(menu_callback.filter(choice_name="players"), state=Check.no_checking)
async def to_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_player_leagues_keyboard(players_callback),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(menu_callback.filter(choice_name="stats"), state=Check.no_checking)
async def to_top(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_stats_leagues_keyboard(stats_callback),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(menu_callback.filter(choice_name="sources"), state=Check.no_checking)
async def to_sources(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:",
                              reply_markup=create_sources_keyboard(),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(menu_callback.filter(choice_name="profile"), state=Check.no_checking)
async def to_profile(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await Check.getting_profile.set()
    await call.message.answer(text="Отправь ссылку на свой профиль на sports.ru:")


@dp.callback_query_handler(menu_callback.filter(choice_name="help"), state=Check.no_checking)
async def to_help(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    answer = ["Для получения справки воспользуйтесь командой /help.",
              "С вопросами и предложениями обращайтесь к @click_here."]
    await call.message.answer(text="\n".join(answer), reply_markup=back_to_menu_keyboard)


@dp.callback_query_handler(menu_callback.filter(choice_name="admin"), state=Check.no_checking)
async def to_admin(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Доступные инструменты:", reply_markup=create_admin_keyboard())


@dp.callback_query_handler(menu_callback.filter(choice_name="back_to_menu"), state=Check.no_checking)
async def back_to_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню:", reply_markup=create_menu_keyboard(call.from_user.id))
