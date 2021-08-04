from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, sources_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.sources_buttons import create_sources_keyboard, create_sources_back_keyboard
from manager_loader import sources_manager


@dp.callback_query_handler(sources_callback.filter(league_name="cancel", ),
                           state=Check.no_checking)
async def to_menu_from_sources(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(call.from_user.id))


@dp.callback_query_handler(sources_callback.filter(league_name="back_to_list", ),
                           state=Check.no_checking)
async def back_to_sources(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_sources_keyboard(),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(sources_callback.filter(name="None", url="None", action=["add", "delete"]),
                           state=Check.no_checking)
async def add_sources(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10) # TODO
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_sources_keyboard(),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(sources_callback.filter(action=["add", "delete"]),
                           state=Check.no_checking)
async def add_sources(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10) # TODO
    await call.message.answer("Доступные чемпионаты:", reply_markup=create_sources_keyboard(),
                              parse_mode=ParseMode.MARKDOWN)


# must be last
@dp.callback_query_handler(sources_callback.filter(), state=Check.no_checking)
async def sources_list(call: CallbackQuery, callback_data: dict):
    print("here")
    print(sources_manager.get_sources(callback_data["league_name"]))

    await call.answer(cache_time=10)
    await call.message.answer(sources_manager.get_sources(callback_data["league_name"]),
                              reply_markup=create_sources_back_keyboard(sources_callback),
                              parse_mode=ParseMode.MARKDOWN)
# @dp.callback_query_handler(sourses_callback.filter(), state=Check.no_checking)
# async def get_coeffs(call: CallbackQuery, callback_data: dict):
#     await call.answer(cache_time=10)
#     await call.message.answer(text=sourses.get_sourses(callback_data["legue_name"]),
#                               reply_markup=sourses_back_keyboard,
#                               parse_mode=ParseMode.MARKDOWN)
