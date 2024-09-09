import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.sports_player import SportsPlayerDAO
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()
    dao = SportsPlayerDAO()
    dao.update_players_all_leagues()
    # dao.update_feature_store()
