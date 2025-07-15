from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class PlayerName(Base):
    __tablename__ = "players_names"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=True, index=True)
    team_name = Column(String, nullable=True, index=True)
    sports_name = Column(String, nullable=True, index=True)
    fbref_name = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    year = Column(String, nullable=True, default="2024")

    def __init__(
        self,
        league_name: Optional[str],
        team_name: Optional[str],
        sports_name: Optional[str],
        fbref_name: Optional[str],
        name: Optional[str],
        timestamp: Optional[datetime],
        year: str = "2024",
    ):
        self.league_name = league_name
        self.team_name = team_name
        self.sports_name = sports_name
        self.fbref_name = fbref_name
        self.name = name
        self.timestamp = timestamp
        self.year = year


    def __repr__(self):
        return f"{self.sports_name}|{self.fbref_name}"
