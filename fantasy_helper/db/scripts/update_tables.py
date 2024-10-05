import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.table import TableDao
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()
    dao = TableDao()
    dao.update_tables_all_leagues()
