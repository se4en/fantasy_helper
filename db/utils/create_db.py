from db.database import create_db, Session
from db.models.coeff import Coeff
from db.models.user import User
from db.models.player import Player
from db.models.leagues_info import League_info
from db.models.player_stats import PlayerStats
from db.models.media_ids import MediaIds
from db.models.sources import Source


def create_database(load_fake_data: bool = True):
    create_db()


if __name__ == "__main__":
    create_database()
