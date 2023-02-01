import logging
from datetime import datetime
from sqlalchemy.orm import Session as SQLSession

from domain.manager import Manager
from db.parse.sports import Sports
from db.database import Session
from db.models.leagues_info import League_info


class LeagueInfoManager(Manager):

    def __init__(self):
        super().__init__()
        self.sports = Sports()

    def update_deadline(self, league_name: str) -> bool:
        """
        Update deadline for league
        """
        logging.info(f"Update deadline for league={league_name}")
        new_deadline = self.sports.get_deadline(league_name)
        if not new_deadline:
            return False

        session: SQLSession = Session()
        league = session.query(League_info).filter(League_info.league == league_name).first()
        if league:
            session.query(League_info).filter(League_info.id == league.id) \
                .update({League_info.deadline: new_deadline})
        else:
            session.add(League_info(league_name, new_deadline))
        session.commit()
        session.close()
        return True

    def update_deadlines(self) -> bool:
        """
        Update deadline for all leagues
        """
        return all([self.update_deadline(x) for x in self.sports.leagues])

    def is_new_round(self, league_name: str) -> bool:
        session: SQLSession = Session()
        league_info = session.query(League_info).filter(League_info.league == league_name).first()
        session.close()
        if not league_info:
            return False
        return datetime.now() > league_info.deadline


if __name__ == "__main__":
    lm = LeagueInfoManager()
    lm.update_deadlines()
