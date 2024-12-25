from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, BigInteger

from fantasy_helper.db.database import Base


class FSPlayersFreeKicks(Base):
    __tablename__ = "fs_players_free_kicks"

    id = Column(BigInteger, primary_key=True)
    league_name = Column(String, nullable=False)
    # common
    name = Column(String, primary_key=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=False)
    # playing time
    games = Column(Integer, nullable=True)
    # pass types
    corner_kicks = Column(Float, nullable=True)
    # shooting
    penalty_goals = Column(Float, nullable=True)
    penalty_shots = Column(Float, nullable=True)
    free_kicks_shots = Column(Float, nullable=True)
    # sports info
    sports_team = Column(String, nullable=True)
    sports_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    percent_ownership = Column(Float, nullable=True)
    percent_ownership_diff = Column(Float, nullable=True)

    def __init__(
        self,
        league_name: str,
        # common
        name: str,
        team: str,
        position: str,
        # playing time
        games: Optional[int],
        # pass types
        corner_kicks: Optional[float],
        # shooting
        penalty_goals: Optional[float],
        penalty_shots: Optional[float],
        free_kicks_shots: Optional[float],
        # sports info
        sports_team: Optional[str] = None,
        sports_name: Optional[str] = None,
        role: Optional[str] = None,
        price: Optional[float] = None,
        percent_ownership: Optional[float] = None,
        percent_ownership_diff: Optional[float] = None
    ):
        self.type = type
        self.league_name = league_name
        # common
        self.name = name
        self.team = team
        self.position = position
        # playing time
        self.games = games
        # pass types
        self.corner_kicks = corner_kicks
        # shooting
        self.penalty_goals = penalty_goals
        self.penalty_shots = penalty_shots
        self.free_kicks_shots = free_kicks_shots
        # sports info
        self.sports_team = sports_team
        self.sports_name = sports_name
        self.role = role
        self.price = price
        self.percent_ownership = percent_ownership
        self.percent_ownership_diff = percent_ownership_diff

    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
