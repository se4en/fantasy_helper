from typing import List
import os.path as path
import datetime
import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()
    CoeffDAO().update_coeffs_all_leagues()
