import os

from dotenv import load_dotenv
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

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

# proxy
PROXY_HOST = str(os.getenv("PROXY_HOST"))
PROXY_PORT = str(os.getenv("PROXY_PORT"))
PROXY_USER = str(os.getenv("PROXY_USER"))
PROXY_PASSWORD = str(os.getenv("PROXY_PASSWORD"))

# open ai
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))

# keycloak
FRONTEND_URL=str(os.getenv("FRONTEND_URL"))
FRONTEND_URL_HTTPS=str(os.getenv("FRONTEND_URL_HTTPS"))
BACKEND_URL=str(os.getenv("FRONTEND_URL"))
BACKEND_URL_HTTPS=str(os.getenv("FRONTEND_URL_HTTPS"))
KEYCLOAK_BASE_URL=str(os.getenv("KEYCLOAK_BASE_URL"))
KEYCLOAK_SERVER_URL=str(os.getenv("KEYCLOAK_SERVER_URL"))                                                                                                                                                                                                                                                                                                                                     
KEYCLOAK_REALM=str(os.getenv("KEYCLOAK_REALM"))                                                                                                                                                                                                                                                                                                                                               
KEYCLOAK_CLIENT_ID=str(os.getenv("KEYCLOAK_CLIENT_ID"))                                                                                                                                                                                                                                                                                                                                     
KEYCLOAK_CLIENT_SECRET=str(os.getenv("KEYCLOAK_CLIENT_SECRET"))

# load leagues info
if not GlobalHydra().is_initialized():
    initialize(config_path=".", version_base=None)
cfg = compose(config_name="config")
leagues = instantiate_leagues(cfg)
