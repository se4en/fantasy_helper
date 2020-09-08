import asyncio

from handlers import dp
from loader import legues, players, users
from utils.notify_admins import on_startup_notify

async def update_coefs(*args):
    if args==():
        for legue in legues:
            legue.update_db()

async def update_players(*args):
    if args==():
        for players_legue in players:
            players_legue.update_db()

async def update_players_after_deadline(*args):
    if args==():    
        for players_legue in players:
            players_legue.create_db()

async def on_startup(at_start=True, timeout=6*60*60):
    await on_startup_notify(dp)
    if at_start:
        await update_coefs()
        await update_players()
    while True:
        await asyncio.sleep(timeout)
        await update_coefs()
        await update_players()