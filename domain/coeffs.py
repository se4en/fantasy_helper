from typing import List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session as SQLSession

from domain.manager import Manager
from db.parse.xbet import XBet
from db.models.coeff import Coeff
from db.database import Session


class CoeffManager(Manager):

    def __init__(self, xbet: XBet):
        self.xbet = xbet

    def __transform_coeffs(self, coeffs: List[Coeff]) -> str:
        pass

    def get_coeffs(self, league_name: str, cur_round: bool) -> str:
        session: SQLSession = Session()
        coeffs = session.query(Coeff).filter(and_(Coeff.league == league_name,
                                                  Coeff.is_cur_round == cur_round))
        if not coeffs:
            return None
        return self.__transform_coeffs(coeffs)

    def update_coeffs(self, league_name: str, new_round: bool = True):
        # delete last round
        if new_round:
            db_session: SQLSession = Session()
            db_session.query(Coeff).filter(Coeff.league == league_name).delete()

        return self.xbet.update_league(league_name, new_round)


if __name__ == "__main__":
    xbet = XBet()
    coeff_manager = CoeffManager(xbet)
    coeff_manager.update_coeffs("Russia")
