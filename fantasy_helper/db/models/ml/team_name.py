from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class TeamName(Base):
    __tablename__ = "team_names"

    id = Column(Integer, primary_key=True)
    sports_team_name = Column(String, nullable=True)
    fbref_team_name = Column(String, nullable=True)
    xbet_team_name = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(
        self,
        sports_team_name: Optional[str],
        fbref_team_name: Optional[str],
        xbet_team_name: Optional[str],
        timestamp: Optional[datetime],
    ):
        self.sports_team_name = sports_team_name
        self.fbref_team_name = fbref_team_name
        self.xbet_team_name = xbet_team_name
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.sports_team_name}|{self.fbref_team_name}|{self.xbet_team_name}"
