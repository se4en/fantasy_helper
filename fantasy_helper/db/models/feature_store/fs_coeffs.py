from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float, JSON

from fantasy_helper.db.database import Base


class FSCoeffs(Base):
    __tablename__ = "fs_coeffs"

    id = Column(Integer, primary_key=True)
    team_name = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    tour_names = Column(JSON, nullable=True)
    tour_numbers = Column(JSON, nullable=True)
    tour_rivals = Column(JSON, nullable=True)
    tour_match_types = Column(JSON, nullable=True)
    tour_attack_coeffs = Column(JSON, nullable=True)
    tour_deffence_coeffs = Column(JSON, nullable=True)
    tour_attack_colors = Column(JSON, nullable=True)
    tour_deffence_colors = Column(JSON, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    def __init__(
        self,
        team_name: str,
        league_name: str,
        tour_names: Optional[List[str]] = None,
        tour_numbers: Optional[List[int]] = None,
        tour_rivals: Optional[List[str]] = None,
        tour_match_types: Optional[List[str]] = None,
        tour_attack_coeffs: Optional[List[float]] = None,
        tour_deffence_coeffs: Optional[List[float]] = None,
        tour_attack_colors: Optional[List[str]] = None,
        tour_deffence_colors: Optional[List[str]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.team_name = team_name
        self.league_name = league_name
        self.tour_names = tour_names
        self.tour_numbers = tour_numbers
        self.tour_rivals = tour_rivals
        self.tour_match_types = tour_match_types
        self.tour_attack_coeffs = tour_attack_coeffs
        self.tour_deffence_coeffs = tour_deffence_coeffs
        self.tour_attack_colors = tour_attack_colors
        self.tour_deffence_colors = tour_deffence_colors
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.team_name} {self.league_name} [{self.tour_names}]"
