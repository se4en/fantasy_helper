import logging
from datetime import datetime
import typing as t

from sqlalchemy.orm import Session as SQLSession
from fantasy_helper.conf.config import ADMINS

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.user import User


class UserDao:
    def __init__(self):
        pass

    def add_user(
        self,
        tg_id: int,
        name: str,
        registration_date: datetime,
        valid: bool = False,
        profile_url: t.Optional[str] = None,
    ) -> None:
        db_session: SQLSession = Session()
        cur_user = db_session.query(User).filter(User.tg_id == tg_id).first()
        if cur_user is None:
            logging.info(f"Add user with name={name}")
            new_user: User = User(tg_id, name, registration_date, valid, profile_url)
            db_session.add(new_user)
        db_session.commit()

    def make_valid(self, tg_id: int) -> None:
        logging.info(f"Make user with tg_id={tg_id} valid")
        db_session: SQLSession = Session()
        db_session.query(User).filter(User.tg_id == tg_id).update({User.valid: True})
        db_session.commit()

    def set_profile_url(self, tg_id: int, profile_url: str) -> None:
        db_session: SQLSession = Session()
        db_session.query(User).filter(User.tg_id == tg_id).update(
            {User.profile_url: profile_url}
        )
        db_session.commit()

    def is_valid(self, tg_id: int) -> bool:
        db_session: SQLSession = Session()
        user = db_session.query(User).filter(User.tg_id == tg_id).first()
        db_session.commit()
        if user is not None and user.valid:
            return True
        return False

    def is_admin(self, tg_id: int) -> bool:
        return tg_id in ADMINS
