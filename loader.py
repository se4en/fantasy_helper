from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from databases.legues_db import LegueDB
from databases.players_db import PlayersDB
from databases.users_db import UsersDB

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
Legues = [
    LegueDB('Russia', 'https://www.fonbet.ru/bets/football/11935/', 'РПЛ')
]
Users = UsersDB()
Players = PlayersDB('Russia', 'https://www.sports.ru/fantasy/football/tournament/31.html')