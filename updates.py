import asyncio

from handlers import dp
from utils.notify_admins import notify_admin


async def update_coeffs():
    pass
    # for league in legues:
    #     legue.update_coefs()


async def update_players():
    pass
    # for players_league in players:
    #     players_league.look_for_updates()


async def on_startup(at_start=False, timeout=3*60*60):
    # timeout for players == 3 hours, for coeffs == 4*timeout
    await notify_admin(dp, "### bot started")
    if at_start:
        await update_players()
        await update_coeffs()
    while True:
        await notify_admin(dp, "### start sleeping")
        await asyncio.sleep(timeout)
        await update_players()
        await update_coeffs()
