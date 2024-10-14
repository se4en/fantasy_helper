from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String

from fantasy_helper.db.database import Base


class FSCalendars(Base):
    __tablename__ = "fs_calendars"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    tour = Column(Integer, nullable=False)
    home_points_color = Column(String, nullable=True)
    away_points_color = Column(String, nullable=True)
    home_goals_color = Column(String, nullable=True)
    away_goals_color = Column(String, nullable=True)
    home_xg_color = Column(String, nullable=True)
    away_xg_color = Column(String, nullable=True)

    def __init__(
        self,
        league_name: str,
        home_team: str,
        away_team: str,
        tour: int,
        home_points_color: Optional[str],
        away_points_color: Optional[str],
        home_goals_color: Optional[str],
        away_goals_color: Optional[str],
        home_xg_color: Optional[str],
        away_xg_color: Optional[str],
    ):
        self.league_name = league_name
        self.home_team = home_team
        self.away_team = away_team
        self.tour = tour
        self.home_points_color = home_points_color
        self.away_points_color = away_points_color
        self.home_goals_color = home_goals_color
        self.away_goals_color = away_goals_color
        self.home_xg_color = home_xg_color
        self.away_xg_color = away_xg_color

    def __repr__(self):
        return f"[{self.tour}] {self.home_team} vs {self.away_team}"
