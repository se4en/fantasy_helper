from aiogram import executor
import asyncio

from handlers import dp
from utils.updates import on_startup
from db.utils.create_db import create_database

if __name__ == '__main__':
    # prepare db
    create_database()
    # run bot
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(at_start=False, timeout=3*60*60))
    loop.create_task(executor.start_polling(dp))
    loop.run_forever()
