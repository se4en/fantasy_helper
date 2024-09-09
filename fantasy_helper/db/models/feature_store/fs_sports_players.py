from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float

from fantasy_helper.db.database import Base


class FSSportsPlayers(Base):
    __tablename__ = "fs_sports_players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    team_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    percent_ownership = Column(Float, nullable=True)
    percent_ownership_diff = Column(Float, nullable=True)

    def __init__(
        self,
        name: str,
        league_name: str,
        team_name: Optional[str],
        role: Optional[str],
        price: Optional[float],
        percent_ownership: Optional[float],
        percent_ownership_diff: Optional[float],
    ):
        self.name = name
        self.league_name = league_name
        self.team_name = team_name
        self.role = role
        self.price = price
        self.percent_ownership = percent_ownership
        self.percent_ownership_diff = percent_ownership_diff

    def __repr__(self):
        return f"{self.name}: {self.percent_ownership}"
