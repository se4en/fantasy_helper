from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from fantasy_helper.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    # id = Column(String(36), primary_key=True)
    email = Column(String, nullable=True)
    email_verified = Column(Boolean, nullable=True)
    name = Column(String, nullable=True)
    preferred_username = Column(String, nullable=True)
    given_name = Column(String, nullable=True)
    family_name = Column(String, nullable=True)
    login_timestamp = Column(DateTime, nullable=True)

    def __init__(
        self,
        id: int,
        email: Optional[str] = None,
        email_verified: Optional[bool] = None,
        name: Optional[str] = None,
        preferred_username: Optional[str] = None,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        login_timestamp: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.email_verified = email_verified
        self.name = name
        self.preferred_username = preferred_username
        self.given_name = given_name
        self.family_name = family_name
        self.login_timestamp = login_timestamp

    def __repr__(self):
        return (
            f"User("
            f"id={self.id}, "
            f"email={self.email}, "
            f"email_verified={self.email_verified}, "
            f"name={self.name}, "            
            f"preferred_username={self.preferred_username}, "
            f"given_name={self.given_name}, "
            f"family_name={self.family_name}"
            f")"
        )
