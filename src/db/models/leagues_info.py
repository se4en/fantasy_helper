from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from datetime import datetime

from db.database import Base


class League_info(Base):
    __tablename__ = 'leagues_info'

    id = Column(Integer, primary_key=True)
    league = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)

    def __init__(self, league: str, deadline: datetime):
        self.league = league
        self.deadline = deadline

    def __repr__(self):
        return f"League={self.league} deadline={self.deadline}"
