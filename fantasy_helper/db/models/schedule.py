import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Date, Float

from fantasy_helper.db.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    gameweek = Column(Integer, nullable=False)
    tour_name = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    year = Column(String, nullable=True, default="2024")

    def __init__(
        self,
        league_name: str,
        timestamp: datetime.datetime,
        home_team: str,
        away_team: str,
        gameweek: int,
        tour_name: Optional[str] = None,
        date: Optional[datetime.date] = None,
        home_goals: Optional[int] = None,
        away_goals: Optional[int] = None,
        year: str = "2024",
    ):
        self.league_name = league_name
        self.timestamp = timestamp
        self.home_team = home_team
        self.away_team = away_team
        self.gameweek = gameweek
        self.tour_name = tour_name
        self.date = date
        self.home_goals = home_goals
        self.away_goals = away_goals
        self.year = year

    def __repr__(self):
        return f"[{self.gameweek}] {self.home_team} vs {self.away_team}"
