from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String

from fantasy_helper.db.database import Base


class FSLineups(Base):
    __tablename__ = "fs_lineups"

    id = Column(Integer, primary_key=True)
    league_name = Column(String, nullable=False)
    team_name = Column(String, nullable=True)
    lineup = Column(String, nullable=True)

    def __init__(
        self,
        league_name: str,
        team_name: Optional[str],
        lineup: Optional[str],
    ):
        self.league_name = league_name
        self.team_name = team_name
        self.lineup = lineup

    def __repr__(self):
        return f"{self.team_name}: {self.lineup}"
