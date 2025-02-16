import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Date, Boolean

from fantasy_helper.db.database import Base


class FbrefSchedule(Base):
    __tablename__ = "fbref_schedules"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    gameweek = Column(Integer, nullable=False)
    date = Column(Date, nullable=True)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    match_url = Column(String, nullable=True)
    match_parsed = Column(Boolean, nullable=True)

    def __init__(
        self,
        league_name: str,
        timestamp: datetime.datetime,
        home_team: str,
        away_team: str,
        gameweek: int,
        date: Optional[datetime.date] = None,
        home_goals: Optional[int] = None,
        away_goals: Optional[int] = None,
        match_url: Optional[str] = None,
        match_parsed: Optional[bool] = None
    ):
        self.league_name = league_name
        self.timestamp = timestamp
        self.home_team = home_team
        self.away_team = away_team
        self.gameweek = gameweek
        self.date = date
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.match_url = match_url
        self.match_parsed = match_parsed

    def __repr__(self):
        return f"[{self.gameweek}] {self.home_team} vs {self.away_team}"
