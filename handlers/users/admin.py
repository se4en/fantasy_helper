from aiogram import types
from aiogram.types import CallbackQuery

from data import config
from loader import dp, users, sourses
from states.checking import Check
from keyboards.inline.callback_datas import admin_callback
from keyboards.inline.menu_buttons import create_menu_keyboard

@dp.callback_query_handler(admin_callback.filter(tool_name="add_sourse",), state=Check.no_checking)
async def add_sourse_start(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await Check.add_sourse.set()
    answer = ["Чтобы добавить источник, отправь в одном сообщении:",
              " - название чемпионата как в списке(!),",
              " - затем на новой строке ссылку,",
              " - затем на новой строке описание."
    ]
    await call.message.answer(text = ('\n').join(answer))

@dp.message_handler(state=Check.add_sourse)
async def add_sourse_finish(message: types.Message):
    await Check.no_checking.set()
    user_message = message.text.split('\n')
    if len(user_message)==3:
        sourses.add_sourse(sourses.unrepresent_name(user_message[0]), user_message[0], user_message[1], user_message[2])    
    elif len(user_message)==2:
        sourses.add_sourse(sourses.unrepresent_name(user_message[0]), user_message[0], user_message[1], "")
    else:
        pass 
    await message.answer(text="Меню:", reply_markup=create_menu_keyboard(message.from_user.id))

@dp.callback_query_handler(admin_callback.filter(tool_name="delete_sourse",), state=Check.no_checking)
async def delete_sourse_start(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await Check.add_sourse.set()
    await call.message.answer(text = "Чтобы удалить источник, отправь ссылку на него.")

@dp.message_handler(state=Check.delete_sourse)
async def delete_sourse_finish(message: types.Message):
    await Check.no_checking.set()
    user_message = message.text.split('\n')
    sourses.delete_sourse(user_message[1])    
    await message.answer(text="Меню:", reply_markup=create_menu_keyboard(message.from_user.id))

@dp.callback_query_handler(admin_callback.filter(tool_name="cancel",), state=Check.no_checking)
async def to_menu_from_admin(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=10)
    await call.message.answer(text="Меню: ", reply_markup=create_menu_keyboard(call.message.from_user.id))