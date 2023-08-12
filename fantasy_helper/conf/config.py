import os

from dotenv import load_dotenv
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra


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
if not GlobalHydra().is_initialized():
    initialize(config_path=".", version_base=None)
cfg = compose(config_name="config")
leagues = instantiate(cfg.leagues)
