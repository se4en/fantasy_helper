from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class Coeff(Base):
    __tablename__ = "coeffs"

    id = Column(Integer, primary_key=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    tour_number = Column(Integer, nullable=True)
    tour_name = Column(String, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    url = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    result_1 = Column(Float, nullable=True)
    result_x = Column(Float, nullable=True)
    result_2 = Column(Float, nullable=True)

    both_score_yes = Column(Float, nullable=True)
    both_score_no = Column(Float, nullable=True)

    total_over_0_5 = Column(Float, nullable=True)
    total_under_0_5 = Column(Float, nullable=True)
    total_over_1 = Column(Float, nullable=True)
    total_under_1 = Column(Float, nullable=True)
    total_over_1_5 = Column(Float, nullable=True)
    total_under_1_5 = Column(Float, nullable=True)
    total_over_2 = Column(Float, nullable=True)
    total_under_2 = Column(Float, nullable=True)
    total_over_2_5 = Column(Float, nullable=True)
    total_under_2_5 = Column(Float, nullable=True)
    total_over_3 = Column(Float, nullable=True)
    total_under_3 = Column(Float, nullable=True)
    total_over_3_5 = Column(Float, nullable=True)
    total_under_3_5 = Column(Float, nullable=True)
    total_over_4 = Column(Float, nullable=True)
    total_under_4 = Column(Float, nullable=True)
    total_over_4_5 = Column(Float, nullable=True)
    total_under_4_5 = Column(Float, nullable=True)

    handicap_1_minus_2_5 = Column(Float, nullable=True)
    handicap_1_minus_2 = Column(Float, nullable=True)
    handicap_1_minus_1_5 = Column(Float, nullable=True)
    handicap_1_minus_1 = Column(Float, nullable=True)
    handicap_1_0 = Column(Float, nullable=True)
    handicap_1_plus_1 = Column(Float, nullable=True)
    handicap_1_plus_1_5 = Column(Float, nullable=True)
    handicap_1_plus_2 = Column(Float, nullable=True)
    handicap_1_plus_2_5 = Column(Float, nullable=True)

    handicap_2_minus_2_5 = Column(Float, nullable=True)
    handicap_2_minus_2 = Column(Float, nullable=True)
    handicap_2_minus_1_5 = Column(Float, nullable=True)
    handicap_2_minus_1 = Column(Float, nullable=True)
    handicap_2_0 = Column(Float, nullable=True)
    handicap_2_plus_1 = Column(Float, nullable=True)
    handicap_2_plus_1_5 = Column(Float, nullable=True)
    handicap_2_plus_2 = Column(Float, nullable=True)
    handicap_2_plus_2_5 = Column(Float, nullable=True)

    total_1_over_0_5 = Column(Float, nullable=True)
    total_1_over_1 = Column(Float, nullable=True)
    total_1_over_1_5 = Column(Float, nullable=True)
    total_1_over_2 = Column(Float, nullable=True)
    total_1_over_2_5 = Column(Float, nullable=True)
    total_1_under_0_5 = Column(Float, nullable=True)
    total_1_under_1 = Column(Float, nullable=True)
    total_1_under_1_5 = Column(Float, nullable=True)
    total_1_under_2 = Column(Float, nullable=True)
    total_1_under_2_5 = Column(Float, nullable=True)

    total_2_over_0_5 = Column(Float, nullable=True)
    total_2_over_1 = Column(Float, nullable=True)
    total_2_over_1_5 = Column(Float, nullable=True)
    total_2_over_2 = Column(Float, nullable=True)
    total_2_over_2_5 = Column(Float, nullable=True)
    total_2_under_0_5 = Column(Float, nullable=True)
    total_2_under_1 = Column(Float, nullable=True)
    total_2_under_1_5 = Column(Float, nullable=True)
    total_2_under_2 = Column(Float, nullable=True)
    total_2_under_2_5 = Column(Float, nullable=True)

    def __init__(
        self,
        home_team: str,
        away_team: str,
        league_name: str,
        start_datetime: datetime,
        tour_number: Optional[int],
        tour_name: Optional[str],
        url: Optional[str],
        timestamp: Optional[datetime],
        result_1: Optional[float],
        result_x: Optional[float],
        result_2: Optional[float],
        both_score_yes: Optional[float],
        both_score_no: Optional[float],
        total_over_0_5: Optional[float],
        total_under_0_5: Optional[float],
        total_over_1: Optional[float],
        total_under_1: Optional[float],
        total_over_1_5: Optional[float],
        total_under_1_5: Optional[float],
        total_over_2: Optional[float],
        total_under_2: Optional[float],
        total_over_2_5: Optional[float],
        total_under_2_5: Optional[float],
        total_over_3: Optional[float],
        total_under_3: Optional[float],
        total_over_3_5: Optional[float],
        total_under_3_5: Optional[float],
        total_over_4: Optional[float],
        total_under_4: Optional[float],
        total_over_4_5: Optional[float],
        total_under_4_5: Optional[float],
        handicap_1_minus_2_5: Optional[float],
        handicap_1_minus_2: Optional[float],
        handicap_1_minus_1_5: Optional[float],
        handicap_1_minus_1: Optional[float],
        handicap_1_0: Optional[float],
        handicap_1_plus_1: Optional[float],
        handicap_1_plus_1_5: Optional[float],
        handicap_1_plus_2: Optional[float],
        handicap_1_plus_2_5: Optional[float],
        handicap_2_minus_2_5: Optional[float],
        handicap_2_minus_2: Optional[float],
        handicap_2_minus_1_5: Optional[float],
        handicap_2_minus_1: Optional[float],
        handicap_2_0: Optional[float],
        handicap_2_plus_1: Optional[float],
        handicap_2_plus_1_5: Optional[float],
        handicap_2_plus_2: Optional[float],
        handicap_2_plus_2_5: Optional[float],
        total_1_over_0_5: Optional[float],
        total_1_over_1: Optional[float],
        total_1_over_1_5: Optional[float],
        total_1_over_2: Optional[float],
        total_1_over_2_5: Optional[float],
        total_1_under_0_5: Optional[float],
        total_1_under_1: Optional[float],
        total_1_under_1_5: Optional[float],
        total_1_under_2: Optional[float],
        total_1_under_2_5: Optional[float],
        total_2_over_0_5: Optional[float],
        total_2_over_1: Optional[float],
        total_2_over_1_5: Optional[float],
        total_2_over_2: Optional[float],
        total_2_over_2_5: Optional[float],
        total_2_under_0_5: Optional[float],
        total_2_under_1: Optional[float],
        total_2_under_1_5: Optional[float],
        total_2_under_2: Optional[float],
        total_2_under_2_5: Optional[float],
    ):
        self.home_team = home_team
        self.away_team = away_team
        self.league_name = league_name
        self.tour_number = tour_number
        self.tour_name = tour_name
        self.url = url
        self.start_datetime = start_datetime
        self.timestamp = timestamp
        self.result_1 = result_1
        self.result_x = result_x
        self.result_2 = result_2
        self.both_score_yes = both_score_yes
        self.both_score_no = both_score_no
        self.total_over_0_5 = total_over_0_5
        self.total_under_0_5 = total_under_0_5
        self.total_over_1 = total_over_1
        self.total_under_1 = total_under_1
        self.total_over_1_5 = total_over_1_5
        self.total_under_1_5 = total_under_1_5
        self.total_over_2 = total_over_2
        self.total_under_2 = total_under_2
        self.total_over_2_5 = total_over_2_5
        self.total_under_2_5 = total_under_2_5
        self.total_over_3 = total_over_3
        self.total_under_3 = total_under_3
        self.total_over_3_5 = total_over_3_5
        self.total_under_3_5 = total_under_3_5
        self.total_over_4 = total_over_4
        self.total_under_4 = total_under_4
        self.total_over_4_5 = total_over_4_5
        self.total_under_4_5 = total_under_4_5
        self.handicap_1_minus_2_5 = handicap_1_minus_2_5
        self.handicap_1_minus_2 = handicap_1_minus_2
        self.handicap_1_minus_1_5 = handicap_1_minus_1_5
        self.handicap_1_minus_1 = handicap_1_minus_1
        self.handicap_1_0 = handicap_1_0
        self.handicap_1_plus_1 = handicap_1_plus_1
        self.handicap_1_plus_1_5 = handicap_1_plus_1_5
        self.handicap_1_plus_2 = handicap_1_plus_2
        self.handicap_1_plus_2_5 = handicap_1_plus_2_5
        self.handicap_2_minus_2_5 = handicap_2_minus_2_5
        self.handicap_2_minus_2 = handicap_2_minus_2
        self.handicap_2_minus_1_5 = handicap_2_minus_1_5
        self.handicap_2_minus_1 = handicap_2_minus_1
        self.handicap_2_0 = handicap_2_0
        self.handicap_2_plus_1 = handicap_2_plus_1
        self.handicap_2_plus_1_5 = handicap_2_plus_1_5
        self.handicap_2_plus_2 = handicap_2_plus_2
        self.handicap_2_plus_2_5 = handicap_2_plus_2_5
        self.total_1_over_0_5 = total_1_over_0_5
        self.total_1_over_1 = total_1_over_1
        self.total_1_over_1_5 = total_1_over_1_5
        self.total_1_over_2 = total_1_over_2
        self.total_1_over_2_5 = total_1_over_2_5
        self.total_1_under_0_5 = total_1_under_0_5
        self.total_1_under_1 = total_1_under_1
        self.total_1_under_1_5 = total_1_under_1_5
        self.total_1_under_2 = total_1_under_2
        self.total_1_under_2_5 = total_1_under_2_5
        self.total_2_over_0_5 = total_2_over_0_5
        self.total_2_over_1 = total_2_over_1
        self.total_2_over_1_5 = total_2_over_1_5
        self.total_2_over_2 = total_2_over_2
        self.total_2_over_2_5 = total_2_over_2_5
        self.total_2_under_0_5 = total_2_under_0_5
        self.total_2_under_1 = total_2_under_1
        self.total_2_under_1_5 = total_2_under_1_5
        self.total_2_under_2 = total_2_under_2
        self.total_2_under_2_5 = total_2_under_2_5

    def __repr__(self):
        return f"{self.home_team} vs {self.away_team} [{self.start_datetime.isoformat(timespec='hours')}]"
