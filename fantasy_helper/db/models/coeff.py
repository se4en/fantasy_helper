from datetime import datetime
import typing as t

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class Coeff(Base):
    __tablename__ = "coeffs"

    id = Column(Integer, primary_key=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    tour = Column(Integer, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    url = Column(String, nullable=True)
    total_1_over_1_5 = Column(Float, nullable=True)
    total_1_under_0_5 = Column(Float, nullable=True)
    total_2_over_1_5 = Column(Float, nullable=True)
    total_2_under_0_5 = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(
        self,
        home_team: str,
        away_team: str,
        league_name: str,
        tour: int,
        start_datetime: datetime,
        url: t.Optional[str],
        total_1_over_1_5: t.Optional[float],
        total_1_under_0_5: t.Optional[float],
        total_2_over_1_5: t.Optional[float],
        total_2_under_0_5: t.Optional[float],
        timestamp: t.Optional[datetime],
    ):
        self.home_team = home_team
        self.away_team = away_team
        self.league_name = league_name
        self.tour = tour
        self.url = url
        self.start_datetime = start_datetime
        self.total_1_over_1_5 = total_1_over_1_5
        self.total_1_under_0_5 = total_1_under_0_5
        self.total_2_over_1_5 = total_2_over_1_5
        self.total_2_under_0_5 = total_2_under_0_5
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.home_team} vs {self.away_team} [{self.start_datetime.isoformat(timespec='hours')}]"
