from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, JSON, DateTime

from fantasy_helper.db.database import Base


class FSCalendars(Base):
    __tablename__ = "fs_calendars"

    id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    tour_names = Column(JSON, nullable=True)
    tour_numbers = Column(JSON, nullable=True)
    tour_rivals = Column(JSON, nullable=True)
    tour_match_types = Column(JSON, nullable=True)
    tour_points_colors = Column(JSON, nullable=True)
    tour_goals_colors = Column(JSON, nullable=True)
    tour_xg_colors = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    def __init__(
        self,
        team_name: str,
        league_name: str,
        tour_names: Optional[List[str]] = None,
        tour_numbers: Optional[List[int]] = None,
        tour_rivals: Optional[List[str]] = None,
        tour_match_types: Optional[List[str]] = None,
        tour_points_colors: Optional[List[str]] = None,
        tour_goals_colors: Optional[List[str]] = None,
        tour_xg_colors: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.team_name = team_name
        self.league_name = league_name
        self.tour_names = tour_names
        self.tour_numbers = tour_numbers
        self.tour_rivals = tour_rivals
        self.tour_match_types = tour_match_types
        self.tour_points_colors = tour_points_colors
        self.tour_goals_colors = tour_goals_colors
        self.tour_xg_colors = tour_xg_colors
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.team_name} [{self.league_name}]"
