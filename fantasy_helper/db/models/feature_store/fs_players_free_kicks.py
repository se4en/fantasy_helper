from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float

from fantasy_helper.db.database import Base


class FSPlayersFreeKicks(Base):
    __tablename__ = "fs_players_free_kicks"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    # common
    name = Column(String, primary_key=False)
    team_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    # playing time
    games = Column(Integer, nullable=True)
    # pass types
    corner_kicks = Column(Float, nullable=True)
    # shooting
    penalty_goals = Column(Float, nullable=True)
    penalty_shots = Column(Float, nullable=True)
    free_kicks_shots = Column(Float, nullable=True)

    def __init__(
        self,
        league_name: str,
        # common
        name: str,
        team_name: str,
        position: str,
        # playing time
        games: Optional[int],
        # pass types
        corner_kicks: Optional[float],
        # shooting
        penalty_goals: Optional[float],
        penalty_shots: Optional[float],
        free_kicks_shots: Optional[float],
    ):
        self.type = type
        self.league_name = league_name
        # common
        self.name = name
        self.team_name = team_name
        self.position = position
        # playing time
        self.games = games
        # pass types
        self.corner_kicks = corner_kicks
        # shooting
        self.penalty_goals = penalty_goals
        self.penalty_shots = penalty_shots
        self.free_kicks_shots = free_kicks_shots

    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
