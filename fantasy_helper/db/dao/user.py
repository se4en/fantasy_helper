import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.user import User
from fantasy_helper.utils.dataclasses import KeycloakUser


utc = timezone.utc


class UserDAO:
    def __init__(self):
        self._default_status = "basic"

    def get_user_by_id(self, id: int) -> Optional[KeycloakUser]:
        db_session: SQLSession = Session()
        user = db_session.query(User).filter(User.id == id).first()
        db_session.close()
        if user is None:
            return None
        else:
            return KeycloakUser(**user.__dict__)

    def add_user(self, user: KeycloakUser) -> None:
        db_session: SQLSession = Session()

        current_timestamp = datetime.now().replace(tzinfo=utc)
        db_session.add(User(
            id=user.id, 
            email=user.email,
            email_verified=user.email_verified,
            name=user.name,
            preferred_username=user.preferred_username,
            given_name=user.given_name,
            family_name=user.family_name,
            login_timestamp=current_timestamp
        ))
            
        db_session.commit()
        db_session.close()
    