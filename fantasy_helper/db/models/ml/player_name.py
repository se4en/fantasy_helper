from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime

from fantasy_helper.db.database import Base


class PlayerName(Base):
    __tablename__ = "players_names"

    id = Column(Integer, primary_key=True)
    sports_name = Column(String, nullable=True, index=True)
    fbref_name = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(
        self,
        sports_name: Optional[str],
        fbref_name: Optional[str],
        timestamp: Optional[datetime],
    ):
        self.sports_name = sports_name
        self.fbref_name = fbref_name
        self.timestamp = timestamp

        if self.sports_name is not None:
            self.name = self.sports_name
        else:
            self.name = self.fbref_name

    def __repr__(self):
        return f"{self.sports_name}|{self.fbref_name}"