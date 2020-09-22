from aiogram import executor
import asyncio

from handlers import dp
from updates import on_startup

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(at_start=True, deadline=False))
    loop.create_task(executor.start_polling(dp))
    loop.run_forever()