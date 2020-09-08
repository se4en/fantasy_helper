from aiogram import executor
from threading import Thread

from handlers import dp
from updates import updater

async def on_startup(dp):
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)

    #from loader import legues, players
    #for legue in legues:
    #    if legue.legue_name == "England":
    #        legue.update_db()

if __name__ == '__main__':
    
    Thread_1 = Thread(target=executor.start_polling, args=(dp,), kwargs={'on_startup' : on_startup})
    Thread_2 = Thread(target=updater)

    Thread_1.start()
    Thread_2.start()

    Thread_1.join()
    Thread_2.join()