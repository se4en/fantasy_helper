from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, DateTime
from datetime import datetime

from db.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)
    registration_date = Column(DateTime, nullable=False)
    valid = Column(Boolean, nullable=False)
    profile_url = Column(String)

    def __init__(self, tg_id: int, name: str, registration_date: datetime,
                 valid: bool = False, profile_url: str = None):
        self.tg_id = tg_id
        self.name = name
        self.registration_date = registration_date
        self.valid = valid
        self.profile_url = profile_url

    def __repr__(self):
        return f"Name={self.name} reg_date={self.registration_date} valid={self.valid}"
