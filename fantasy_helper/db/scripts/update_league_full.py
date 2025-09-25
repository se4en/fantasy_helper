import asyncio
from typing import List
import os.path as path
import datetime
import sys

from loguru import logger

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.db.utils.create_db import create_db
from fantasy_helper.utils.dataclasses import LeagueInfo
from fantasy_helper.db.dao.table import TableDao
from fantasy_helper.db.dao.schedule import ScheduleDao
from fantasy_helper.db.dao.fbref_schedule import FbrefScheduleDao
from fantasy_helper.db.dao.feature_store.fs_calendar import FSCalendarsDAO
from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.dao.sports_player import SportsPlayerDAO
from fantasy_helper.db.dao.ml.naming import NamingDAO
from fantasy_helper.db.dao.player import PlayerDAO


async def main(league_name: str):
    schedule_dao = ScheduleDao()
    table_dao = TableDao()
    calendar_dao = FSCalendarsDAO()
    fbref_schedule_dao = FbrefScheduleDao()
    coeff_dao = CoeffDAO()
    sports_player_dao = SportsPlayerDAO()
    naming_dao = NamingDAO()
    player_dao = PlayerDAO()
    
    # update actual fbref names and players
    player_dao.update_actual_players_stats(league_name)
    naming_dao.update_league_naming(league_name)

    # update main tables
    schedule_dao.update_schedules(league_name)
    table_dao.update_tables(league_name)
    calendar_dao.update_calendar(league_name)
    fbref_schedule_dao.update_schedule(league_name)

    await coeff_dao.update_coeffs(league_name)
    
    # disable for separate script
    # sports_player_dao.update_players(league_name)

    # disable for player_dao.update_feature_store
    # player_dao.update_players_stats(league_name)

    # update feature stores
    coeff_dao.update_feature_store(league_name)
    # disable for separate script
    # sports_player_dao.update_feature_store(league_name)
    player_dao.update_feature_store(league_name)

    import gc
    gc.collect()


if __name__ == "__main__":
    create_db()
    cfg = load_config(config_path="../../conf", config_name="config")
    all_leagues: List[LeagueInfo] = instantiate_leagues(cfg)

    # add league name parameter
    if len(sys.argv) > 1:
        league_name = sys.argv[1]
        asyncio.run(main(league_name))
    else:
        for league in all_leagues:
            asyncio.run(main(league.name))
