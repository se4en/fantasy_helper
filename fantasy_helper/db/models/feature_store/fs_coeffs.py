from datetime import datetime
import typing as t

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class FSCoeffs(Base):
    __tablename__ = "fs_coeffs"

    id = Column(Integer, primary_key=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    tour_number = Column(Integer, nullable=False)
    tour_name = Column(String, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    url = Column(String, nullable=True)
    total_1_over_1_5 = Column(Float, nullable=True)
    total_1_under_0_5 = Column(Float, nullable=True)
    total_2_over_1_5 = Column(Float, nullable=True)
    total_2_under_0_5 = Column(Float, nullable=True)

    def __init__(
        self,
        home_team: str,
        away_team: str,
        league_name: str,
        tour_number: int,
        tour_name: t.Optional[str],
        start_datetime: datetime,
        url: t.Optional[str],
        total_1_over_1_5: t.Optional[float],
        total_1_under_0_5: t.Optional[float],
        total_2_over_1_5: t.Optional[float],
        total_2_under_0_5: t.Optional[float],
    ):
        self.home_team = home_team
        self.away_team = away_team
        self.league_name = league_name
        self.tour_number = tour_number
        self.tour_name = tour_name
        self.start_datetime = start_datetime
        self.url = url
        self.total_1_over_1_5 = total_1_over_1_5
        self.total_1_under_0_5 = total_1_under_0_5
        self.total_2_over_1_5 = total_2_over_1_5
        self.total_2_under_0_5 = total_2_under_0_5

    def __repr__(self):
        return f"{self.home_team} vs {self.away_team} [{self.start_datetime.isoformat(timespec='hours')}]"
