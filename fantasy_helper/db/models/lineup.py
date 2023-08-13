from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class Lineup(Base):
    __tablename__ = "lineups"

    id = Column(Integer, primary_key=True)
    update_id = Column(Integer, primary_key=False)
    league_name = Column(String, nullable=False)
    team_name = Column(String, nullable=True)
    lineup = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(
        self,
        update_id: int,
        league_name: str,
        team_name: Optional[str],
        lineup: Optional[str],
        timestamp: Optional[datetime],
    ):
        self.update_id = update_id
        self.league_name = league_name
        self.team_name = team_name
        self.lineup = lineup
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.team_name}: {self.lineup}"
