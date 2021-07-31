from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, ParseMode

from keyboards.inline.stats_buttons import create_stats_leagues_keyboard, create_stats_league_back_keyboard, \
    create_stats_league_menu_keyboard
from loader import bot, dp
from manager_loader import player_stats_manager
from states.checking import Check
from keyboards.inline.callback_datas import stats_callback
from keyboards.inline.menu_buttons import create_menu_keyboard


@dp.callback_query_handler(stats_callback.filter(league_name="cancel", ),
                           state=Check.no_checking)
async def to_menu_from_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ",
                              reply_markup=create_menu_keyboard(call.from_user.id))


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
    photo_id = player_stats_manager.get_players_shoots_id(callback_data["league_name"],
                                                          callback_data["last_5"] == "True")
    if not photo_id:
        await call.message.answer(text="Данная статистика сейчас недоступна(",
                                  reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                                 callback_data["league_name"]),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        if callback_data["last_5"] == "True":
            stats_title = "<b>Статистика за 5 последних туров</b>"
        else:
            stats_title = "<b>Статистика за 3 последних тура</b>"
        await bot.send_photo(call.from_user.id, photo_id,
                             caption='\n'.join([stats_title, "Уд/И - <i>среднее число ударов за 90 мин</i>",
                                                "УдC/Уд - <i>процент попаданий в створ</i>"]),
                             reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                            callback_data["league_name"]),
                             parse_mode=ParseMode.HTML)


@dp.callback_query_handler(stats_callback.filter(type="xg"), state=Check.no_checking)
async def get_xg_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    photo_id = player_stats_manager.get_xg_id(callback_data["league_name"],
                                              callback_data["last_5"] == "True")
    if not photo_id:
        await call.message.answer(text="Данная статистика сейчас недоступна(",
                                  reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                                 callback_data["league_name"]),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        if callback_data["last_5"] == "True":
            stats_title = "<b>Статистика за 5 последних туров</b>"
        else:
            stats_title = "<b>Статистика за 3 последних тура</b>"
        await bot.send_photo(call.from_user.id, photo_id,
                             caption=stats_title,
                             reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                            callback_data["league_name"]),
                             parse_mode=ParseMode.HTML)


@dp.callback_query_handler(stats_callback.filter(type="xg_xa"), state=Check.no_checking)
async def get_xg_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    photo_id = player_stats_manager.get_xg_xa_id(callback_data["league_name"],
                                                 callback_data["last_5"] == "True")
    if not photo_id:
        await call.message.answer(text="Данная статистика сейчас недоступна(",
                                  reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                                 callback_data["league_name"]),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        if callback_data["last_5"] == "True":
            stats_title = "<b>Статистика за 5 последних туров</b>"
        else:
            stats_title = "<b>Статистика за 3 последних тура</b>"
        await bot.send_photo(call.from_user.id, photo_id,
                             caption=stats_title,
                             reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                            callback_data["league_name"]),
                             parse_mode=ParseMode.HTML)


@dp.callback_query_handler(stats_callback.filter(type="sca"), state=Check.no_checking)
async def get_xg_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    photo_id = player_stats_manager.get_sca_id(callback_data["league_name"],
                                               callback_data["last_5"] == "True")
    if not photo_id:
        await call.message.answer(text="Данная статистика сейчас недоступна(",
                                  reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                                 callback_data["league_name"]),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        if callback_data["last_5"] == "True":
            stats_title = "<b>Статистика за 5 последних туров</b>"
        else:
            stats_title = "<b>Статистика за 3 последних тура</b>"
        await bot.send_photo(call.from_user.id, photo_id,
                             caption='\n'.join([stats_title, "sca/И - <i>Атакующие действия, непосредственно ведущих \
                             к удару, такие как пасы, дриблинг и заработанные фолы</i>", "gca/И - <i>Атакующие \
                             действия, непосредственно ведущие к голу ...</i>"]),
                             reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                            callback_data["league_name"]),
                             parse_mode=ParseMode.HTML)


@dp.callback_query_handler(stats_callback.filter(type="gca"), state=Check.no_checking)
async def get_xg_stats(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    photo_id = player_stats_manager.get_gca_id(callback_data["league_name"],
                                               callback_data["last_5"] == "True")
    if not photo_id:
        await call.message.answer(text="Данная статистика сейчас недоступна(",
                                  reply_markup=create_stats_league_menu_keyboard(stats_callback,
                                                                                 callback_data["league_name"]),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        if callback_data["last_5"] == "True":
            stats_title = "<b>Статистика за 5 последних туров</b>"
        else:
            stats_title = "<b>Статистика за 3 последних тура</b>"
        await bot.send_photo(call.from_user.id, photo_id,
                             caption='\n'.join([stats_title, "gca/И - <i>Атакующие действия, непосредственно ведущих \
                             к голу, такие как пасы, дриблинг и заработанные фолы</i>", "sca/И - <i>Атакующие \
                             действия, непосредственно ведущие к удару ...</i>"]),
                             reply_markup=create_stats_league_menu_keyboard(stats_callback,
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
