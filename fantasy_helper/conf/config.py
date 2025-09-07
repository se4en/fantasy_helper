import os
import ast
from typing import Any, List

from dotenv import load_dotenv
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.utils.common import load_config, instantiate_leagues


def parse_env_list(var_name: str) -> List[Any]:
    value = os.getenv(var_name)
    print("value", value)
    if not value or not value.strip():
        print("fork 0")
        return []
    
    value = value.strip()
    
    if value.startswith('[') and value.endswith(']'):
        print("fork 1")
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            pass
    
    if value.startswith('[') and value.endswith(']'):
        print("fork 2")
        inner_content = value[1:-1].strip()
        if not inner_content:
            return []
        
        items = []
        for item in inner_content.split(','):
            item = item.strip()
            if not item:
                continue
            
            try:
                parsed_item = ast.literal_eval(item)
            except (SyntaxError, ValueError):
                parsed_item = item
            
            items.append(parsed_item)
        
        return items
    elif ',' in value:
        print("fork 3")
        items = []
        for item in value.split(','):
            item = item.strip()
            if not item:
                continue
            
            try:
                parsed_item = ast.literal_eval(item)
            except (SyntaxError, ValueError):
                parsed_item = item
            
            items.append(parsed_item)
        
        return items
    else:
        print("fork 4")
        try:
            return [ast.literal_eval(value)]
        except (SyntaxError, ValueError):
            return [value]


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
PROXY_HOSTS = parse_env_list("PROXY_HOSTS")
PROXY_PORTS = parse_env_list("PROXY_PORTS")
PROXY_USERS = parse_env_list("PROXY_USERS")
PROXY_PASSWORDS = parse_env_list("PROXY_PASSWORDS")

# open ai
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY"))
OPENROUTER_API_KEY = str(os.getenv("OPENROUTER_API_KEY"))

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
