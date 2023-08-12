import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.lineup import LineupDAO
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()
    LineupDAO().update_lineups_all_leagues()
