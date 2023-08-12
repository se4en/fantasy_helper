from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from fantasy_helper.conf import config
from db.dao.coeffs import CoeffDao
from db.dao.medias import MediaDao
from db.dao.sources import SourceDao
from db.dao.squads import SquadDao
from db.dao.users import UserDao

# from


bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


# TODO load urls from config and create parsers


user_dao = CoeffDao()
user_dao = UserDao()
user_dao = UserDao()
user_dao = UserDao()
user_dao = UserDao()
