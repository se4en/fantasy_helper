import logging
import typing as t

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.squad import Squad


class SquadDao:
    def __init__(self):
        pass

    def set_squad(self, user_id: int, league: str, squad_id: int) -> None:
        db_session: SQLSession = Session()
        squad = (
            db_session.query(Squad)
            .filter(and_(Squad.user_id == user_id, Squad.league == league))
            .first()
        )
        if squad is None:
            new_squad = Squad(user_id, league, squad_id)
            db_session.add(new_squad)
        else:
            squad.squad_id = squad_id
        db_session.commit()

    def get_squad(self, user_id: int, league: str) -> t.Optional[int]:
        db_session: SQLSession = Session()
        squad = (
            db_session.query(Squad)
            .filter(and_(Squad.user_id == user_id, Squad.league == league))
            .first()
        )
        db_session.commit()
        if squad is None:
            return None
        else:
            return squad.squad_id
