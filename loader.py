from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from db.parse.sports import Sports
from db.parse.xbet import XBet
from db.parse.fbref import FbrefParser
from domain.coeffs import CoeffManager
from domain.leagues_info import LeagueInfoManager
from domain.player_stats import PlayerStatsManager
from domain.players import PlayerManager
from domain.users import UserManager


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

xbet = XBet()
sports = Sports()
fbref = FbrefParser()
coeff_manager = CoeffManager(xbet)
user_manager = UserManager()
player_manager = PlayerManager()
player_stats_manager = PlayerStatsManager()
league_info_manager = LeagueInfoManager()
