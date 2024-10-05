from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    gameweek = Column(Integer, nullable=False)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)

    def __init__(
        self,
        league_name: str,
        timestamp: datetime,
        home_team: str,
        away_team: str,
        gameweek: int,
        home_goals: Optional[int],
        away_goals: Optional[int],
    ):
        self.league_name = league_name
        self.timestamp = timestamp
        self.home_team = home_team
        self.away_team = away_team
        self.gameweek = gameweek
        self.home_goals = home_goals
        self.away_goals = away_goals

    def __repr__(self):
        return f"[{self.gameweek}] {self.home_team} vs {self.away_team}"
