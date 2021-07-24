from sqlalchemy import Column
from sqlalchemy import Integer, String

from db.database import Base


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    league = Column(String, nullable=False)
    team = Column(String, nullable=False)
    amplua = Column(String, nullable=False)
    old_popularity = Column(Integer, nullable=False)
    dif_popularity = Column(Integer, nullable=False)

    def __init__(self, name: str, league: str, team: str, amplua: str,
                 old_popularity: int, dif_popularity: int):
        self.name = name
        self.league = league
        self.team = team
        self.amplua = amplua
        self.old_popularity = old_popularity
        self.dif_popularity = dif_popularity

    def __repr__(self):
        return f"Name={self.name} team={self.team} dif_pop={self.dif_popularity}"
