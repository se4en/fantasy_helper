from datetime import datetime
import typing as t

from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, DateTime

from fantasy_helper.db.database import Base


class User(Base):
    __tablename__ = "users"

    tg_id = Column(Integer, primary_key=True)
    name = Column(String)
    registration_date = Column(DateTime, nullable=False)
    valid = Column(Boolean, nullable=False)
    profile_url = Column(String, nullable=True)

    def __init__(
        self,
        tg_id: int,
        name: str,
        registration_date: datetime,
        valid: bool = False,
        profile_url: t.Optional[str] = None,
    ):
        self.tg_id = tg_id
        self.name = name
        self.registration_date = registration_date
        self.valid = valid
        self.profile_url = profile_url

    def __repr__(self):
        return f"Name={self.name} reg_date={self.registration_date} valid={self.valid}"
