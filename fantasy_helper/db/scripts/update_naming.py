import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.utils.create_db import create_db
from fantasy_helper.db.dao.ml.naming import NamingDAO


if __name__ == "__main__":
    create_db()
    dao = NamingDAO()
    dao.update_naming_all_leagues()
