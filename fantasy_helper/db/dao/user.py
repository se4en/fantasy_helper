import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.user import User


utc = timezone.utc


class UserDao:
    def __init__(self):
        self._default_status = "basic"

    def login(
        self,
        id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[str] = None,
        login_timestamp: Optional[datetime] = None,
        last_timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        db_session: SQLSession = Session()

        user_status = self._default_status if status is None else status
        cur_user = db_session.query(User).filter(User.id == id).first()
        current_timestamp = datetime.now().replace(tzinfo=utc)
        if cur_user is None:
            db_session.add(User(
                id, 
                first_name=first_name,
                last_name=last_name,
                username=username,
                phone=phone,
                status=user_status,
                login_timestamp=current_timestamp,
                last_timestamp=current_timestamp
            ))
        else:
            user_status = cur_user.status
            cur_user.last_timestamp = current_timestamp
        db_session.commit()
        db_session.close()

        return user_status
    