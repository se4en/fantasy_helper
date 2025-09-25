import sys

from loguru import logger

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.sports_player import SportsPlayerDAO
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()

    logger.info(f"Start update sports players")
    dao = SportsPlayerDAO()
    dao.update_players_all_leagues()
    dao.update_feature_store_all_leagues()
    logger.info(f"Finish update sports players")
