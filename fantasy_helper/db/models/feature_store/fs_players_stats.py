from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, BigInteger

from fantasy_helper.db.database import Base


class FSPlayersStats(Base):
    __tablename__ = "fs_players_stats"

    id = Column(BigInteger, primary_key=True)
    league_name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    # common
    name = Column(String, primary_key=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=True)
    # playing time
    games = Column(Integer, nullable=True)
    games_all = Column(Integer, nullable=True)
    minutes = Column(Integer, nullable=True)
    # shooting
    goals = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    shots_on_target = Column(Integer, nullable=True)
    average_shot_distance = Column(Float, nullable=True)
    xg = Column(Float, nullable=True)
    xg_np = Column(Float, nullable=True)
    xg_xa = Column(Float, nullable=True)
    xg_np_xa = Column(Float, nullable=True)
    # passing
    assists = Column(Integer, nullable=True)
    xa = Column(Float, nullable=True)
    key_passes = Column(Integer, nullable=True)
    passes_into_penalty_area = Column(Integer, nullable=True)
    crosses_into_penalty_area = Column(Integer, nullable=True)
    # possesion
    touches_in_attacking_third = Column(Integer, nullable=True)
    touches_in_attacking_penalty_area = Column(Integer, nullable=True)
    carries_in_attacking_third = Column(Integer, nullable=True)
    carries_in_attacking_penalty_area = Column(Integer, nullable=True)
    # shot creation
    sca = Column(Integer, nullable=True)
    gca = Column(Integer, nullable=True)
    # miscellaneous
    ball_recoveries = Column(Integer, nullable=True)
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
        type: Optional[str] = None,
        games: Optional[float] = None,
        games_all: Optional[float] = None,
        minutes: Optional[float] = None,
        # shooting
        goals: Optional[float] = None,
        shots: Optional[float] = None,
        shots_on_target: Optional[float] = None,
        average_shot_distance: Optional[float] = None,
        xg: Optional[float] = None,
        xg_np: Optional[float] = None,
        xg_xa: Optional[float] = None,
        xg_np_xa: Optional[float] = None,
        # passing
        assists: Optional[float] = None,
        xa: Optional[float] = None,
        key_passes: Optional[float] = None,
        passes_into_penalty_area: Optional[float] = None,
        crosses_into_penalty_area: Optional[float] = None,
        # pass types
        touches_in_attacking_third: Optional[float] = None,
        touches_in_attacking_penalty_area: Optional[float] = None,
        carries_in_attacking_third: Optional[float] = None,
        carries_in_attacking_penalty_area: Optional[float] = None,
        # shot creation
        sca: Optional[float] = None,
        gca: Optional[float] = None,
        # miscellaneous
        ball_recoveries: Optional[int] = None,
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
        self.games_all = games_all
        self.minutes = minutes
        # shooting
        self.goals = goals
        self.shots = shots
        self.shots_on_target = shots_on_target
        self.average_shot_distance = average_shot_distance
        self.xg = xg
        self.xg_np = xg_np
        self.xg_xa = xg_xa
        self.xg_np_xa = xg_np_xa
        # passing
        self.assists = assists
        self.xa = xa
        self.key_passes = key_passes
        self.passes_into_penalty_area = passes_into_penalty_area
        self.crosses_into_penalty_area = crosses_into_penalty_area
        # possesion
        self.touches_in_attacking_third = touches_in_attacking_third
        self.touches_in_attacking_penalty_area = touches_in_attacking_penalty_area
        self.carries_in_attacking_third = carries_in_attacking_third
        self.carries_in_attacking_penalty_area = carries_in_attacking_penalty_area
        # shot creation
        self.sca = sca
        self.gca = gca
        # miscellaneous
        self.ball_recoveries = ball_recoveries
        # sports info
        self.sports_team = sports_team
        self.sports_name = sports_name
        self.role = role
        self.price = price
        self.percent_ownership = percent_ownership
        self.percent_ownership_diff = percent_ownership_diff

    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
