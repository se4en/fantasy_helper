import asyncio

from handlers import dp
from loader import legues, players, sourses, users
from utils.notify_admins import on_startup_notify

async def update_coefs(*args):
    if args==():
        for legue in legues:
            legue.update_db()

async def update_players(*args):
    pass

async def update_players_after_deadline(*args):
    pass

async def on_startup(at_start=True, timeout=1*60*60):
    await on_startup_notify(dp)
    if at_start:
        #await update_coefs()
        #await update_players()
        pass
    while True:
        print("one")
        await asyncio.sleep(timeout)
        print("two")
        await update_coefs()
        await update_players_after_deadline()