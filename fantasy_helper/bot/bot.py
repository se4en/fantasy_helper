import logging
import asyncio

from aiogram import executor

from bot.utils.updates import on_startup
from bot.handlers import dp
from db.utils.create_db import create_database


if __name__ == "__main__":
    logging.basicConfig(filename="bot_history.log", level=logging.INFO)
    # prepare db
    create_database()
    # run bot
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(False))
    loop.create_task(executor.start_polling(dp))
    loop.run_forever()
