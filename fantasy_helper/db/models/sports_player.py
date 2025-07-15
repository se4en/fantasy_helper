from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class SportsPlayer(Base):
    __tablename__ = "sports_players"

    id = Column(Integer, primary_key=True)
    sports_id = Column(Integer, primary_key=False)
    name = Column(String, nullable=False)
    league_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    tour = Column(Integer, nullable=True)
    role = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    percent_ownership = Column(Float, nullable=True)
    team_name = Column(String, nullable=True)
    place = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    average_score = Column(Float, nullable=True)
    goals = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    goals_conceded = Column(Integer, nullable=True)
    yellow_cards = Column(Integer, nullable=True)
    red_cards = Column(Integer, nullable=True)
    field_minutes = Column(Integer, nullable=True)
    saves = Column(Integer, nullable=True)
    year = Column(String, nullable=True, default="2024")

    def __init__(
        self,
        sports_id: int,
        name: str,
        league_name: str,
        timestamp: datetime,
        tour: Optional[int],
        role: Optional[str],
        price: Optional[float],
        percent_ownership: Optional[float],
        team_name: Optional[str],
        place: Optional[int],
        score: Optional[int],
        average_score: Optional[float],
        goals: Optional[int],
        assists: Optional[int],
        goals_conceded: Optional[int],
        yellow_cards: Optional[int],
        red_cards: Optional[int],
        field_minutes: Optional[int],
        saves: Optional[int],
        year: str = "2024",
    ):
        self.sports_id = sports_id
        self.name = name
        self.league_name = league_name
        self.tour = tour
        self.timestamp = timestamp
        self.role = role
        self.price = price
        self.percent_ownership = percent_ownership
        self.team_name = team_name
        self.place = place
        self.score = score
        self.average_score = average_score
        self.goals = goals
        self.assists = assists
        self.goals_conceded = goals_conceded
        self.yellow_cards = yellow_cards
        self.red_cards = red_cards
        self.field_minutes = field_minutes
        self.saves = saves
        self.year = year

    def __repr__(self):
        return f"{self.name} [{self.role}] from {self.team_name}"
