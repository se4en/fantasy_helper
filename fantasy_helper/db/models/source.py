import typing as t

from sqlalchemy import Column
from sqlalchemy import Integer, String

from fantasy_helper.db.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    league = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(String)

    def __init__(
        self, name: str, league: str, url: str, description: t.Optional[str] = None
    ):
        self.name = name
        self.league = league
        self.url = url
        self.description = description

    def __repr__(self):
        return f"Name={self.name} league={self.league} url={self.url}"
