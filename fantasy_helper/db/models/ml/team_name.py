from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class TeamName(Base):
    __tablename__ = "teams_names"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=True, index=True)
    sports_name = Column(String, nullable=True, index=True)
    fbref_name = Column(String, nullable=True, index=True)
    xbet_name = Column(String, nullable=True, index=True)
    betcity_name = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    year = Column(String, nullable=True, default="2024")

    def __init__(
        self,
        league_name: Optional[str],
        sports_name: Optional[str],
        fbref_name: Optional[str],
        xbet_name: Optional[str],
        betcity_name: Optional[str],
        name: Optional[str],
        timestamp: Optional[datetime],
        year: str = "2024",
    ):
        self.league_name = league_name
        self.sports_name = sports_name
        self.fbref_name = fbref_name
        self.xbet_name = xbet_name
        self.betcity_name = betcity_name
        self.name = name
        self.timestamp = timestamp
        self.year = year

    def __repr__(self):
        return f"{self.sports_name}|{self.fbref_name}|{self.xbet_name}|{self.betcity_name}"
