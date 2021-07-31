import asyncio
import datetime

from handlers import dp
from utils.notify_admins import notify_admin
from manager_loader import league_info_manager, coeff_manager, player_manager, player_stats_manager, xbet


async def update_coeffs(league_name: str):
    coeff_manager.update_coeffs(league_name)


async def update_players(league_name: str, new_round: bool):
    player_manager.update_league(league_name, new_round)


async def update_players_stats(league_name: str, new_round: bool):
    player_stats_manager.update_league(league_name, new_round)


async def update_all():
    await notify_admin(dp, "[INFO] start update all")
    for league_name in xbet.leagues:
        new_round = league_info_manager.is_new_round(league_name)
        if new_round:
            league_info_manager.update_deadline(league_name)

        await update_players(league_name, new_round)
        await update_players_stats(league_name, new_round)
        await update_coeffs(league_name)
    await notify_admin(dp, "[INFO] finish update all")


async def update_players_leagues():
    await notify_admin(dp, "[INFO] start update players")
    for league in xbet.leagues:
        await update_players(league, False)
    await notify_admin(dp, "[INFO] finish update players")


async def on_startup(upd_at_start=True, timeout: int = 1 * 60 * 60,
                     upd_time: datetime.datetime = datetime.datetime.strptime("03:00:00", "%H:%M:%S")):
    upd_today = upd_at_start
    await notify_admin(dp, "[INFO] bot started")
    while True:
        await asyncio.sleep(timeout)
        # restart upd_today
        if upd_today and datetime.datetime.now().time() < upd_time.time():
            upd_today = False
        if (not upd_today) and datetime.datetime.now().time() > upd_time.time():
            await update_all()
            upd_today = True
        # else:
        #     await update_players_leagues()
