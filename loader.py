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
    LegueDB('Russia', 'https://www.fonbet.ru/bets/football/11935/', \
            'https://www.sports.ru/fantasy/football/team/points/2220643.html', 'РПЛ'),
    LegueDB('France', 'https://www.fonbet.ru/bets/football/11920/', \
            'https://www.sports.ru/fantasy/football/team/points/2232514.html', 'Лига 1'),
    LegueDB('England', 'https://www.fonbet.ru/bets/football/11918/', \
            'https://www.sports.ru/fantasy/football/team/points/2243551.html', 'АПЛ'),
    LegueDB('Germany', 'https://www.fonbet.ru/bets/football/11916/', \
            'https://www.sports.ru/fantasy/football/team/points/2243555.html', 'Бундеслига'),
    LegueDB('Spain', 'https://www.fonbet.ru/bets/football/11922/', \
            'https://www.sports.ru/fantasy/football/team/points/2243562.html', 'ЛаЛига'),
    LegueDB('Netherlands', 'https://www.fonbet.ru/bets/football/12967/', \
            'https://www.sports.ru/fantasy/football/team/points/2243575.html', 'Эрдевизи'),
    LegueDB('Championship', 'https://www.fonbet.ru/bets/football/12018/', \
            'https://www.sports.ru/fantasy/football/team/points/2243558.html', 'Чемпионшип'),
    LegueDB('Turckey', 'https://www.fonbet.ru/bets/football/12973/', \
            'https://www.sports.ru/fantasy/football/team/points/2243571.html', 'Суперлига'),
    LegueDB('Italy', 'https://www.fonbet.ru/bets/football/11924/', \
            'https://www.sports.ru/fantasy/football/team/points/2258596.html', 'Серия А'),
    LegueDB('Portugal', 'https://www.fonbet.ru/bets/football/11939', \
            'https://www.sports.ru/fantasy/football/team/points/2258098.html', 'Португалия'),
    LegueDB('UEFA_1', 'https://www.fonbet.ru/bets/football/15290', \
            'https://www.sports.ru/fantasy/football/team/points/2283074.html', 'Лига Чемпионов'),
    LegueDB('UEFA_2', 'https://www.fonbet.ru/bets/football/15290', \
            'https://www.sports.ru/fantasy/football/team/points/2284228.html', 'Лига Европы')
]
users = UsersDB()
players = [
    PlayersDB('Russia', 'https://www.sports.ru/fantasy/football/tournament/31.html', 'РПЛ'),
    PlayersDB('France', 'https://www.sports.ru/fantasy/football/tournament/51.html', 'Лига 1'),
    PlayersDB('England', 'https://www.sports.ru/fantasy/football/tournament/52.html', 'АПЛ'),
    PlayersDB('Germany', 'https://www.sports.ru/fantasy/football/tournament/50.html', 'Бундеслига'),
    PlayersDB('Spain', 'https://www.sports.ru/fantasy/football/tournament/49.html', 'ЛаЛига'),
    PlayersDB('Netherlands', 'https://www.sports.ru/fantasy/football/tournament/54.html', 'Эрдевизи'),
    PlayersDB('Championship', 'https://www.sports.ru/fantasy/football/tournament/205.html', 'Чемпионшип'),
    PlayersDB('Turckey', 'https://www.sports.ru/fantasy/football/tournament/246.html', 'Суперлига'),
    PlayersDB('Italy', 'https://www.sports.ru/fantasy/football/tournament/48.html', 'Серия А'),
    PlayersDB('Portugal', 'https://www.sports.ru/fantasy/football/tournament/207.html', 'Португалия'),
    PlayersDB('UEFA_1', 'https://www.sports.ru/fantasy/football/tournament/57.html', 'Лига Чемпионов'),
    PlayersDB('UEFA_2', 'https://www.sports.ru/fantasy/football/tournament/56.html', 'Лига Европы')
]

sourses = Sourses()