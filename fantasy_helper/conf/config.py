import os

from dotenv import load_dotenv

from fantasy_helper.utils.common import load_config, instantiate_leagues


load_dotenv()

# tg bot
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PASSWORD = str(os.getenv("PASSWORD"))
ADMINS = list(map(int, str(os.getenv("ADMINS")).split(",")))

# pg db
POSTGRES_USER = str(os.getenv("POSTGRES_USER"))
POSTGRES_PASSWORD = str(os.getenv("POSTGRES_PASSWORD"))
POSTGRES_DB = str(os.getenv("POSTGRES_DB"))
POSTGRES_URI = str(os.getenv("POSTGRES_URI"))
DATABASE_URI = str(os.getenv("DATABASE_URI"))

# load leagues info
cfg = load_config(config_path=".", config_name="config")
leagues = instantiate_leagues(cfg)
