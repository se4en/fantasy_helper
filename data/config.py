import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PASSWORD = str(os.getenv("PASSWORD"))
ADMINS = list(map(int, str(os.getenv("ADMINS")).split(' ')))
DATABASE_URI = str(os.getenv("DATABASE_URI"))

admins = ADMINS
