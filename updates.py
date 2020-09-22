import asyncio

from handlers import dp
from loader import legues, players, users
from utils.notify_admins import notify_admin

async def update_coefs(*args):
    if args==():
        for legue in legues:
            await notify_admin(dp, f"### start coefs {legue.legue_name} updating ...")
            legue.update_db()
            await notify_admin(dp, f"### coefs {legue.legue_name} updated")

async def update_players(*args):
    if args==():
        for players_legue in players:
            await notify_admin(dp, f"### start players {players_legue.legue_name} updating ...")
            players_legue.update_db()
            await notify_admin(dp, f"### players {players_legue.legue_name} updated")

async def update_players_after_deadline(*args):
    if args==():    
        for players_legue in players:
            await notify_admin(dp, f"### start players {players_legue.legue_name} deadline updating ...")
            players_legue.update_db(new_round=True)
            await notify_admin(dp, f"### players {players_legue.legue_name} deadline updated")

async def on_startup(at_start=False, deadline=False, timeout=12*60*60):
    await notify_admin(dp, "### bot started")
    if deadline:
        await update_players_after_deadline()
        if at_start:
            update_coefs()
    elif at_start:
        await update_players()
        #await update_coefs()
    while True:
        await notify_admin(dp, "### start sleeping")
        await asyncio.sleep(timeout)
        await notify_admin(dp, "### end sleeping")
        await update_players()
        await update_coefs()
