import sys

sys.path.insert(0, "/fantasy_helper")

from fantasy_helper.db.dao.table import TableDao
from fantasy_helper.db.dao.schedule import ScheduleDao
from fantasy_helper.db.dao.feature_store.fs_calendar import FSCalendarsDAO
from fantasy_helper.db.utils.create_db import create_db


if __name__ == "__main__":
    create_db()

    schedule_dao = ScheduleDao()
    table_dao = TableDao()
    calendar_dao = FSCalendarsDAO()

    schedule_dao.update_schedules_all_leagues()
    table_dao.update_tables_all_leagues()
    calendar_dao.update_calendar_all_leagues()
