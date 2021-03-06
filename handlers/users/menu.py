from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from loader import users, legues, players
from keyboards.inline.menu_buttons import create_menu_keyboard, back_to_menu_keyboard
from keyboards.inline.callback_datas import menu_callback, coefs_callback, players_callback
from keyboards.inline.country_buttons import create_country_keyboard
from keyboards.inline.admin_buttons import admin_keyboard
from keyboards.inline.sourses_buttons import create_sourses_keyboard
from states.checking import Check

@dp.callback_query_handler(menu_callback.filter(choice_name="coefs"), state=Check.no_checking)
async def to_coefs(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", 
        reply_markup=create_country_keyboard(legues, coefs_callback), 
        parse_mode=ParseMode.MARKDOWN
    )

@dp.callback_query_handler(menu_callback.filter(choice_name="players"), state=Check.no_checking)
async def to_players(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", 
        reply_markup=create_country_keyboard(players, players_callback), 
        parse_mode=ParseMode.MARKDOWN
    ) 

@dp.callback_query_handler(menu_callback.filter(choice_name="top"), state=Check.no_checking)
async def to_top(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Эта функция скоро станет доступна\nМеню:", 
        reply_markup=create_menu_keyboard(call.message.from_user.id), 
        parse_mode=ParseMode.MARKDOWN
    ) 

@dp.callback_query_handler(menu_callback.filter(choice_name="sourses"), state=Check.no_checking)
async def to_sourses(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", 
        reply_markup=create_sourses_keyboard(), 
        parse_mode=ParseMode.MARKDOWN
    ) 

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
    await call.message.answer(text=("\n").join(answer), reply_markup=back_to_menu_keyboard)

@dp.callback_query_handler(menu_callback.filter(choice_name="admin"), state=Check.no_checking)
async def to_admin(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Доступные инструменты:", reply_markup=admin_keyboard)

@dp.callback_query_handler(menu_callback.filter(choice_name="back_to_menu"), state=Check.no_checking)
async def back_to_menu(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню:", reply_markup=create_menu_keyboard(call.message.from_user.id))