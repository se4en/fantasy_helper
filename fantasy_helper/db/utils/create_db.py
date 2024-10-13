from fantasy_helper.db.database import Base, db_engine
from fantasy_helper.db.models.squad import Squad
from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.source import Source
from fantasy_helper.db.models.user import User
from fantasy_helper.db.models.lineup import Lineup
from fantasy_helper.db.models.player import Player
from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.models.table import Table
from fantasy_helper.db.models.schedule import Schedule
from fantasy_helper.db.models.feature_store.fs_coeffs import FSCoeffs
from fantasy_helper.db.models.feature_store.fs_lineups import FSLineups
from fantasy_helper.db.models.feature_store.fs_players_stats import FSPlayersStats
from fantasy_helper.db.models.feature_store.fs_players_free_kicks import (
    FSPlayersFreeKicks,
)
from fantasy_helper.db.models.feature_store.fs_sports_players import FSSportsPlayers
from fantasy_helper.db.models.feature_store.fs_calendars import FSCalendars


def create_db():
    Base.metadata.create_all(db_engine)


if __name__ == "__main__":
    create_db()
