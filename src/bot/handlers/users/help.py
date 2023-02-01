from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from src.loader import dp
from states.checking import Check


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Начать диалог',
        '/help - Получить справку',
        '\nЭлементы меню:',
        'Коэффициенты - кэффы 1.5тб и 0.5тм',
        'Популярные игроки - разница между популярностью игрока после последнего дэдлайна и на настоящее время',
        'Лучшие игроки - кэффы на гол',
        'Привязать профиль - привязать аккаунт на sports.ru'   
    ]
    await message.answer('\n'.join(text))
