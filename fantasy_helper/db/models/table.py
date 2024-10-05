from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    rank = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    draws = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    goals_for = Column(Integer, nullable=False)
    goals_against = Column(Integer, nullable=False)
    xg_for = Column(Float, nullable=True)
    xg_against = Column(Float, nullable=True)

    def __init__(
        self,
        league_name: str,
        team_name: str,
        timestamp: datetime,
        rank: int,
        wins: int,
        draws: int,
        losses: int,
        points: int,
        goals_for: int,
        goals_against: int,
        xg_for: Optional[float],
        xg_against: Optional[float],
    ):
        self.league_name = league_name
        self.team_name = team_name
        self.timestamp = timestamp
        self.rank = rank
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.points = points
        self.goals_for = goals_for
        self.goals_against = goals_against
        self.xg_for = xg_for
        self.xg_against = xg_against

    def __repr__(self):
        return f"{self.team_name}: {self.rank}"
