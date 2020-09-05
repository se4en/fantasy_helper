import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
PASSWORD = str(os.getenv("PASSWORD"))
ADMIN_1 = int(os.getenv("ADMIN_1"))

admins = [ 
    ADMIN_1,
]