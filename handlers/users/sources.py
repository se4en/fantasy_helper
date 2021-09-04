from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from loader import dp
from states.checking import Check
from keyboards.inline.callback_datas import menu_callback, sources_callback
from keyboards.inline.menu_buttons import create_menu_keyboard
from keyboards.inline.sources_buttons import create_sources_keyboard, create_sources_back_keyboard, \
    create_sources_league_keyboard, create_delete_source_keyboard
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


@dp.callback_query_handler(sources_callback.filter(action="add"), state=Check.no_checking)
async def add_new_source(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer(cache_time=10)

    await Check.set_name.set()
    async with state.proxy() as data:
        data['league'] = callback_data['league_name']

    await call.message.answer("Введите название (коротко):", parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Check.set_name)
async def set_new_name(message: types.Message, state: FSMContext):
    await Check.set_url.set()
    async with state.proxy() as data:
        data['name'] = message.text

    await message.answer("Введите url:", parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Check.set_url)
async def set_new_url(message: types.Message, state: FSMContext):
    await Check.set_description.set()
    async with state.proxy() as data:
        data['url'] = message.text

    await message.answer("Введите описание:", parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=Check.set_description)
async def set_new_description(message: types.Message, state: FSMContext):
    # save source
    async with state.proxy() as data:
        sources_manager.add_source(data['name'], data['league'], data['url'], message.text)
    await Check.no_checking.set()
    # await state.finish()
    await message.answer(sources_manager.get_sources_repr(data['league']),
                         reply_markup=create_sources_league_keyboard(sources_callback,
                                                                     data['league']),
                         parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


@dp.callback_query_handler(sources_callback.filter(action="delete"), state=Check.no_checking)
async def delete_source(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer("Выберите источник для удаления:",
                              reply_markup=create_delete_source_keyboard(sources_callback,
                                                                         callback_data['league_name']),
                              parse_mode=ParseMode.MARKDOWN)


@dp.callback_query_handler(sources_callback.filter(action="to_delete"), state=Check.no_checking)
async def delete_source(call: CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer(cache_time=10)
    league_name = sources_manager.delete_source_by_id(int(callback_data['league_name']))
    await call.message.answer(sources_manager.get_sources_repr(league_name),
                              reply_markup=create_sources_league_keyboard(sources_callback, league_name),
                              parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


# must be last
@dp.callback_query_handler(sources_callback.filter(), state=Check.no_checking)
async def sources_list(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(sources_manager.get_sources_repr(callback_data["league_name"]),
                              reply_markup=create_sources_league_keyboard(sources_callback,
                                                                          callback_data["league_name"]),
                              parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
