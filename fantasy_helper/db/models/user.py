from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, DateTime

from fantasy_helper.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, nullable=True)
    login_timestamp = Column(DateTime, nullable=True)
    last_timestamp = Column(DateTime, nullable=True)

    def __init__(
        self,
        id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None,
        login_timestamp: Optional[datetime] = None,
        last_timestamp: Optional[datetime] = None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.status = status
        self.login_timestamp = login_timestamp
        self.last_timestamp = last_timestamp

    def __repr__(self):
        return f"first_name={self.first_name} last_name={self.last_name}"
