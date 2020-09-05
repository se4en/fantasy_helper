from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from databases.legues_db import LegueDB
from databases.players_db import PlayersDB
from databases.users_db import UsersDB
from databases.sourses_db import Sourses

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
legues = [
    LegueDB('Russia', 'https://www.fonbet.ru/bets/football/11935/', 'РПЛ'),
    LegueDB('France', 'https://www.fonbet.ru/bets/football/11920/', 'Лига 1')
]
users = UsersDB()
players = [
    PlayersDB('Russia', 'https://www.sports.ru/fantasy/football/tournament/31.html', 'РПЛ')
]
sourses = Sourses()