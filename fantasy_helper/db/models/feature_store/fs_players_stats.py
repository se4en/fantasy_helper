from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float, BigInteger

from fantasy_helper.db.database import Base


class FSPlayersStats(Base):
    __tablename__ = "fs_players_stats"

    id = Column(BigInteger, primary_key=True)
    type = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    # common
    name = Column(String, primary_key=False)
    team = Column(String, nullable=False)
    position = Column(String, nullable=False)
    # playing time
    games = Column(Integer, nullable=True)
    minutes = Column(Float, nullable=True)
    # shooting
    goals = Column(Float, nullable=True)
    shots = Column(Float, nullable=True)
    shots_on_target = Column(Float, nullable=True)
    average_shot_distance = Column(Float, nullable=True)
    xg = Column(Float, nullable=True)
    xg_np = Column(Float, nullable=True)
    xg_xa = Column(Float, nullable=True)
    xg_np_xa = Column(Float, nullable=True)
    # passing
    assists = Column(Float, nullable=True)
    xa = Column(Float, nullable=True)
    key_passes = Column(Float, nullable=True)
    passes_into_penalty_area = Column(Float, nullable=True)
    crosses_into_penalty_area = Column(Float, nullable=True)
    # possesion
    touches_in_attacking_third = Column(Float, nullable=True)
    touches_in_attacking_penalty_area = Column(Float, nullable=True)
    carries_in_attacking_third = Column(Float, nullable=True)
    carries_in_attacking_penalty_area = Column(Float, nullable=True)
    # shot creation
    sca = Column(Float, nullable=True)
    gca = Column(Float, nullable=True)
    # sports info
    sports_team = Column(String, nullable=True)
    sports_name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    percent_ownership = Column(Float, nullable=True)
    percent_ownership_diff = Column(Float, nullable=True)

    def __init__(
        self,
        type: str,
        league_name: str,
        # common
        name: str,
        team: str,
        position: str,
        # playing time
        games: Optional[float],
        minutes: Optional[float],
        # shooting
        goals: Optional[float],
        shots: Optional[float],
        shots_on_target: Optional[float],
        average_shot_distance: Optional[float],
        xg: Optional[float],
        xg_np: Optional[float],
        xg_xa: Optional[float],
        xg_np_xa: Optional[float],
        # passing
        assists: Optional[float],
        xa: Optional[float],
        key_passes: Optional[float],
        passes_into_penalty_area: Optional[float],
        crosses_into_penalty_area: Optional[float],
        # pass types
        touches_in_attacking_third: Optional[float],
        touches_in_attacking_penalty_area: Optional[float],
        carries_in_attacking_third: Optional[float],
        carries_in_attacking_penalty_area: Optional[float],
        # shot creation
        sca: Optional[float],
        gca: Optional[float],
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
        # sports info
        self.sports_team = sports_team
        self.sports_name = sports_name
        self.role = role
        self.price = price
        self.percent_ownership = percent_ownership
        self.percent_ownership_diff = percent_ownership_diff

    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
