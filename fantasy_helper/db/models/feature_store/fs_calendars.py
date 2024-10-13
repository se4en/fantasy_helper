from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Float

from fantasy_helper.db.database import Base


class FSCalendars(Base):
    __tablename__ = "fs_calendars"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    tour = Column(Integer, nullable=False)
    home_points_score = Column(Float, nullable=True)
    away_points_score = Column(Float, nullable=True)
    home_xg_score = Column(Float, nullable=True)
    away_xg_score = Column(Float, nullable=True)

    def __init__(
        self,
        league_name: str,
        home_team: str,
        away_team: str,
        tour: int,
        home_points_score: Optional[float],
        away_points_score: Optional[float],
        home_xg_score: Optional[float],
        away_xg_score: Optional[float],
    ):
        self.league_name = league_name
        self.home_team = home_team
        self.away_team = away_team
        self.tour = tour
        self.home_points_score = home_points_score
        self.away_points_score = away_points_score
        self.home_xg_score = home_xg_score
        self.away_xg_score = away_xg_score

    def __repr__(self):
        return f"[{self.tour}] {self.home_team} vs {self.away_team}"
