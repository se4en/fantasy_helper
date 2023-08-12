from datetime import datetime
from typing import List, Literal, Optional, Tuple
import os.path as path
from datetime import timezone

from sqlalchemy import and_, func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.utils import instantiate
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text

from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.xbet import XbetParser
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo
from fantasy_helper.utils.prettify import emojize_coeff


utc = timezone.utc


class CoeffDAO:
    TEAM1_MAX_LEN = 9
    TEAM2_MAX_LEN = 9

    def __init__(self):
        # initialize(config_path="../../conf", version_base=None)
        cfg = compose(config_name="config")
        self._leagues: List[LeagueInfo] = instantiate(cfg.leagues)

        self._xbet_parser = XbetParser(leagues=self._leagues)
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
        )

    @staticmethod
    def __format_coeff_value(coeff_value: float) -> str:
        return emojize(
            emojize_coeff(coeff_value) + " " + str(coeff_value) + "  "
            if len(str(coeff_value)) == 4
            else emojize_coeff(coeff_value) + " " + (str(coeff_value) + "0")[:4] + "  "
        )

    def __coeff_to_str(
        self, coeff: Coeff, attack: bool = True
    ) -> Tuple[float, Tuple[str]]:
        # get needed coeff value
        if attack:
            home_team_coeff_value = coeff.total_1_over_1_5
            away_team_coeff_value = coeff.total_2_over_1_5
        else:
            home_team_coeff_value = coeff.total_1_under_0_5
            away_team_coeff_value = coeff.total_2_under_0_5

        # emojize coeff value
        home_team_coeff_str = CoeffDAO.__format_coeff_value(home_team_coeff_value)
        away_team_coeff_str = CoeffDAO.__format_coeff_value(away_team_coeff_value)

        # format team name
        home_team_name = coeff.home_team[
            : min(len(coeff.home_team), self.TEAM1_MAX_LEN)
        ]
        away_team_name = coeff.away_team[
            : min(len(coeff.away_team), self.TEAM2_MAX_LEN)
        ]

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

    def __coeffs_to_str(self, coeffs: List[Coeff], is_cur_tour: bool) -> str:
        if is_cur_tour:
            result = [emojize(":one: Текущий тур:\n")]
        else:
            result = [emojize(":two: Следующий тур:\n")]

        result += ["\U0001F5E1 Атакующий потенциал:\n"]
        attack_coeffs = [self.__coeff_to_str(coeff, attack=True) for coeff in coeffs]
        sorted_attack_coeffs = sorted(attack_coeffs, key=lambda x: x[0])
        result += list(map(lambda x: x[1], sorted_attack_coeffs))

        result += ["\n\U0001F6E1 Защитный потенциал:\n"]
        defend_coeffs = [self.__coeff_to_str(coeff, attack=False) for coeff in coeffs]
        sorted_defend_coeffs = sorted(defend_coeffs, key=lambda x: x[0])
        result += list(map(lambda x: x[1], sorted_defend_coeffs))

        return "\n".join(result)

    def get_coeffs_message(
        self, league: str, is_cur_tour: bool = True
    ) -> Optional[str]:
        # get current tour
        cur_tour = self._sports_parser.get_cur_tour(league)
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

    def get_coeffs(
        self, league_name: str, tour: Literal["cur", "next"] = "cur"
    ) -> List[MatchInfo]:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        tour_number = tour_info["number"] if tour == "cur" else tour_info["number"] + 1
        db_session: SQLSession = Session()

        cur_tour_rows = (
            db_session.query(Coeff)
            .filter(and_(Coeff.league_name == league_name, Coeff.tour == tour_number))
            .subquery()
        )

        grouped_by_matches = db_session.query(
            cur_tour_rows,
            func.rank()
            .over(
                order_by=cur_tour_rows.c.timestamp.desc(),
                partition_by=(cur_tour_rows.c.home_team, cur_tour_rows.c.away_team),
            )
            .label("rnk"),
        ).subquery()

        cur_tour_matches = (
            db_session.query(grouped_by_matches)
            .filter(grouped_by_matches.c.rnk == 1)
            .all()
        )

        result = [
            MatchInfo(
                url=match.url,
                league_name=match.league_name,
                home_team=match.home_team,
                away_team=match.away_team,
                start_datetime=match.start_datetime,
                total_1_over_1_5=match.total_1_over_1_5,
                total_2_over_1_5=match.total_2_over_1_5,
                total_1_under_0_5=match.total_1_under_0_5,
                total_2_under_0_5=match.total_2_under_0_5,
            )
            for match in cur_tour_matches
        ]

        db_session.commit()
        db_session.close()

        return result

    def get_tour_number(self, league_name: str) -> int:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        return tour_info["number"]

    def update_coeffs(self, league_name: str) -> None:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        if tour_info is None:
            return None
        matches = self._xbet_parser.get_league_matches(league_name)
        db_session: SQLSession = Session()

        for match in matches:
            if match.start_datetime < tour_info["deadline"]:
                match_tour = tour_info["number"] - 1
            elif match.start_datetime < tour_info["next_tour_deadline"]:
                match_tour = tour_info["number"]
            else:
                match_tour = tour_info["number"] + 1

            db_session.add(
                Coeff(
                    **match.__dict__,
                    tour=match_tour,
                    timestamp=datetime.now().replace(tzinfo=utc),
                )
            )

        db_session.commit()
        db_session.close()

    def update_coeffs_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_coeffs(league.name)
