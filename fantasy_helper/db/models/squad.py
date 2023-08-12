from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String

from fantasy_helper.db.database import Base


class Squad(Base):
    __tablename__ = "squads"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.tg_id"))
    league = Column(String, nullable=False)
    squad_id = Column(Integer, nullable=False)

    def __init__(
        self,
        user_id: int,
        league: str,
        squad_id: int,
    ):
        self.user_id = user_id
        self.league = league
        self.squad_id = squad_id

    def __repr__(self):
        return f"Tg_id={self.user_id} league={self.league} squad_id={self.squad_id}"
