import sys

from loguru import logger

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.fbref_schedule import FbrefScheduleDao
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()

    logger.info(f"Start update fbref schedules")
    dao = FbrefScheduleDao()
    dao.update_schedules_all_leagues()
    logger.info(f"Finish update fbref schedules")
