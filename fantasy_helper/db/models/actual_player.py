from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class ActualPlayer(Base):
    __tablename__ = "actual_players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    league_name = Column(String, nullable=True, index=True)
    team_name = Column(String, nullable=True, index=True)
    position = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    def __init__(
        self,
        name: Optional[str],
        league_name: Optional[str],
        team_name: Optional[str],
        position: Optional[str],
        timestamp: Optional[datetime]
    ):
        self.name = name
        self.league_name = league_name
        self.team_name = team_name
        self.position = position
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
