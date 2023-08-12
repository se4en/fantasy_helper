from fantasy_helper.db.database import Base, db_engine
from fantasy_helper.db.models.squad import Squad
from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.source import Source
from fantasy_helper.db.models.user import User


def create_db():
    Base.metadata.create_all(db_engine)


if __name__ == "__main__":
    create_db()
