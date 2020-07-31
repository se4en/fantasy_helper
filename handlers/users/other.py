from aiogram import types

from loader import dp

@dp.message_handler()
async def bot_echo(message: types.Message):
    text = [
        'Я не знаю такой команды(',
        'Для получения справки воспользуйтесь командой /help'
    ]
    await message.answer(('\n').join(text))