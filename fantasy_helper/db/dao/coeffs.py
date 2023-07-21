from datetime import datetime
import typing as t

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text

from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.xbet import XbetParser
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import MatchInfo
from fantasy_helper.utils.prettify import emojize_coeff

TEAM1_MAX_LEN = 9
TEAM2_MAX_LEN = 9


class CoeffDao:
    def __init__(self, xbet_parser: XbetParser, sports_parser: SportsParser):
        self.__xbet_parser = xbet_parser
        self.__sports_parser = sports_parser

    @staticmethod
    def __format_coeff_value(coeff_value: float) -> str:
        return emojize(
            emojize_coeff(coeff_value) + " " + str(coeff_value) + "  "
            if len(str(coeff_value)) == 4
            else emojize_coeff(coeff_value) + " " + (str(coeff_value) + "0")[:4] + "  "
        )

    @staticmethod
    def __coeff_to_str(
        coeff: Coeff, attack: bool = True
    ) -> t.Tuple[float, t.Tuple[str]]:
        # get needed coeff value
        if attack:
            home_team_coeff_value = coeff.total_1_over_1_5
            away_team_coeff_value = coeff.total_2_over_1_5
        else:
            home_team_coeff_value = coeff.total_1_under_0_5
            away_team_coeff_value = coeff.total_2_under_0_5

        # emojize coeff value
        home_team_coeff_str = CoeffDao.__format_coeff_value(home_team_coeff_value)
        away_team_coeff_str = CoeffDao.__format_coeff_value(away_team_coeff_value)

        # format team name
        home_team_name = coeff.home_team[: min(len(coeff.home_team), TEAM1_MAX_LEN)]
        away_team_name = coeff.away_team[: min(len(coeff.away_team), TEAM2_MAX_LEN)]

        home_team_coeff = (
            home_team_coeff_value,
            text(
                home_team_coeff_str,
                f"<b>{home_team_name} [д] </b>",
                f"<i>vs {away_team_name}</i>",
                sep="",
            ),
        )
        away_team_coeff = (
            away_team_coeff_value,
            text(
                away_team_coeff_str,
                f"<b>{away_team_name} [г] </b>",
                f"<i>vs {home_team_name}</i>",
                sep="",
            ),
        )

        return home_team_coeff, away_team_coeff

    @staticmethod
    def __coeffs_to_str(coeffs: t.List[Coeff], is_cur_tour: bool) -> str:
        if is_cur_tour:
            result = [emojize(":one: Текущий тур:\n")]
        else:
            result = [emojize(":two: Следующий тур:\n")]

        result += ["\U0001F5E1 Атакующий потенциал:\n"]
        attack_coeffs = [
            CoeffDao.__coeff_to_str(coeff, attack=True) for coeff in coeffs
        ]
        sorted_attack_coeffs = sorted(attack_coeffs, key=lambda x: x[0])
        result += list(map(lambda x: x[1], sorted_attack_coeffs))

        result += ["\n\U0001F6E1 Защитный потенциал:\n"]
        defend_coeffs = [
            CoeffDao.__coeff_to_str(coeff, attack=False) for coeff in coeffs
        ]
        sorted_defend_coeffs = sorted(defend_coeffs, key=lambda x: x[0])
        result += list(map(lambda x: x[1], sorted_defend_coeffs))

        return "\n".join(result)

    def get_coeffs_message(
        self, league: str, is_cur_tour: bool = True
    ) -> t.Optional[str]:
        # get current tour
        cur_tour = self.__sports_parser.get_cur_tour(league)
        if cur_tour is None:
            # TODO logging
            return None
        if not is_cur_tour:
            cur_tour += 1

        db_session: SQLSession = Session()
        coeffs = db_session.query(Coeff).filter(
            and_(Coeff.league == league, Coeff.tour == cur_tour)
        )
        if not coeffs:
            return None
        db_session.close()

        return self.__coeffs_to_str(coeffs, is_cur_tour)

    def update_coeffs(self, league: str) -> None:
        def update_coeff(match: MatchInfo) -> None:
            nonlocal league, cur_tour, cur_datetime, db_session

            db_session.query(Coeff).filter(
                and_(
                    Coeff.league == league,
                    Coeff.tour == cur_tour,
                    Coeff.home_team == match.home_team,
                    Coeff.away_team == match.away_team,
                )
            ).update(
                {
                    "total_1_over_1_5": match.total_1_over_1_5,
                    "total_1_under_0_5": match.total_1_under_0_5,
                    "total_2_over_1_5": match.total_2_over_1_5,
                    "total_2_under_0_5": match.total_2_under_0_5,
                    "timestamp": cur_datetime,
                }
            )

        tour_mathces_count = self.__sports_parser.get_cur_tour_mathces_count(league)
        tour_matches = self.__xbet_parser.get_league_matches(league)
        cur_datetime = datetime.now()
        cur_tour = self.__sports_parser.get_cur_tour(league)

        if tour_mathces_count is None or cur_tour is None:
            # TODO logging
            return None

        db_session: SQLSession = Session()
        match_id = 0
        # update matches for current tour
        while match_id < tour_mathces_count:
            update_coeff(tour_matches[match_id])
            match_id += 1
        # update matches for next tour
        cur_tour += 1
        while match_id < len(tour_matches):
            update_coeff(tour_matches[match_id])
            match_id += 1
        db_session.commit()
        db_session.close()
