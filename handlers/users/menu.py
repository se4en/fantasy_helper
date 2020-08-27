from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from loader import users, legues, players
from keyboards.inline.menu_buttons import menu_keyboard, back_to_menu_keyboard
from keyboards.inline.callback_datas import menu_callback, coefs_callback, players_callback
from keyboards.inline.country_buttons import create_country_keyboard
from states.checking import Check

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(menu_callback.filter(choice_name="coefs"))
async def to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", 
        reply_markup=create_country_keyboard(legues, coefs_callback), 
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(menu_callback.filter(choice_name="players"))
async def to_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", 
        reply_markup=create_country_keyboard(players, players_callback), 
        parse_mode=ParseMode.MARKDOWN
    ) 

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(menu_callback.filter(choice_name="profile"))
async def bot_geturl(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await Check.getting_profile.set()
    await call.message.answer(text="Отправь ссылку на свой профиль на sports.ru:")

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(menu_callback.filter(choice_name="help"))
async def to_help(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    answer = ["Для получения справки воспользуйтесь командой /help.",
              "С вопросами и предложениями обращайтесь к @click_here."]
    await call.message.answer(text=("\n").join(answer), reply_markup=back_to_menu_keyboard)

@dp.callback_query_handler(state=Check.no_checking)
@dp.callback_query_handler(menu_callback.filter(choice_name="back_to_menu"))
async def back_to_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню:", reply_markup=menu_keyboard)