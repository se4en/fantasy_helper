import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN, PROXY_URL, PROXY_AUTH

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
'''
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nОтправь мне фото, и я верну его размером 256x256!")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("У меня есть команды:\n/help - получить помощь\n/start - начать обмен фото")

@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)

@dp.message_handler(content_types=types.ContentType.PHOTO)
async def photo_handler(msg: types.Message):
    file = await bot.get_file(file_id=msg.photo[-1].file_id)
    await file.download('photo1.jpg')
    #await msg.reply_photo()
'''
if __name__ == '__main__':
    executor.start_polling(dp)