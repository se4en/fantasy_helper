import asyncio

from handlers import dp
from utils.notify_admins import notify_admin
from loader import league_info_manager, coeff_manager, player_manager, player_stats_manager, xbet


async def update_coeffs(league_name: str):
    coeff_manager.update_coeffs(league_name)


async def update_players(league_name: str, new_round: bool):
    player_manager.update_league(league_name, new_round)


async def update_players_stats(league_name: str, new_round: bool):
    player_stats_manager.update_league(league_name, new_round)


async def update_league(league_name: str, upd_cnt: int):
    new_round = league_info_manager.is_new_round(league_name)
    if new_round:
        league_info_manager.update_deadline(league_name)
    if upd_cnt % 12 == 0:
        await update_coeffs(league_name)
        await update_players_stats(league_name, new_round)
    await update_players(league_name, new_round)


async def update(upd_cnt: int):
    for league in xbet.leagues:
        await update_league(league, upd_cnt)


async def on_startup(at_start=False, timeout=1*60*60):
    # timeout for players == 1 hour, for coeffs & stats == 12*timeout
    upd_cnt = 1
    await notify_admin(dp, "### bot started")
    if at_start:
        await update(upd_cnt)
        upd_cnt += 1
    while True:
        await notify_admin(dp, "### start sleeping")
        await asyncio.sleep(timeout)
        await update(upd_cnt)
        if upd_cnt == 12:
            upd_cnt = 1

