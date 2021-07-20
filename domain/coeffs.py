from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text

from domain.manager import Manager
from db.parse.xbet import XBet
from db.models.coeff import Coeff
from db.database import Session


class CoeffManager(Manager):

    def __init__(self, xbet: XBet):
        super().__init__()
        self.xbet = xbet

    def __transform_coeff(self, coeff: Coeff, attack: bool = True):
        coeff_value = coeff.more_1_5 if attack else coeff.clean_sheet
        em_coeff = emojize(self.emojize_coeff(coeff_value) + " " + str(coeff_value) + "  "
                           if len(str(coeff_value)) == 4
                           else self.emojize_coeff(coeff_value) + " " +
                                (str(coeff_value) + "0")[:4] + "  ")
        match_label = "[д]" if coeff.is_home else "[г]"

        TEAM1_MAX_LEN = 8
        if len(coeff.team) <= TEAM1_MAX_LEN + 4:
            team1 = f"<b>{coeff.team} </b>"
        else:
            team1 = f"<b>{coeff.team[:TEAM1_MAX_LEN]} {match_label} </b>"

        TEAM2_MAX_LEN = 8
        if len(coeff.team_against) <= TEAM2_MAX_LEN:
            team2 = f"<i>vs {coeff.team_against}</i>"
        else:
            team2 = f"<i>vs {coeff.team_against[:TEAM2_MAX_LEN]}</i>"
        return text(em_coeff, team1, team2, sep="")

    def __transform_coeffs(self, coeffs: List[Coeff]) -> str:
        result: List[str] = ["\U0001F5E1 Атакующий потенциал:\n", ]
        coeffs.sort(key=lambda cf: cf.more_1_5)
        result += [self.__transform_coeff(cf, attack=True) for cf in coeffs]

        result += ["\n\U0001F6E1 Защитный потенциал:\n"]
        coeffs.sort(key=lambda cf: cf.clean_sheet)
        result += [self.__transform_coeff(cf, attack=False) for cf in coeffs]

        return '\n'.join(result)

    def get_coeffs(self, league_name: str, cur_round: bool) -> str:
        session: SQLSession = Session()
        coeffs = session.query(Coeff).filter(and_(Coeff.league == league_name,
                                                  Coeff.is_cur_round == cur_round))
        if not coeffs:
            return ""
        coeffs_list: List[Coeff] = [cf for cf in coeffs]
        return self.__transform_coeffs(coeffs_list)

    def update_coeffs(self, league_name: str, new_round: bool = True):
        # delete last round
        if new_round:
            db_session: SQLSession = Session()
            db_session.query(Coeff).filter(Coeff.league == league_name).delete()
            db_session.commit()

        return self.xbet.update_league(league_name, new_round)

    @staticmethod
    def get_leagues():
        xbet = XBet()
        return list(xbet.leagues.keys())


if __name__ == "__main__":
    xbet = XBet()
    coeff_manager = CoeffManager(xbet)
    # coeff_manager.update_coeffs("Russia", new_round=True)
    print("Cur round:")
    print(coeff_manager.get_coeffs("Russia", cur_round=True))
    print("Next round:")
    print(coeff_manager.get_coeffs("Russia", cur_round=False))
