from datetime import datetime
from typing import List, Literal, Optional, Tuple
import os.path as path
from datetime import timezone

from sqlalchemy import and_, func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.xbet import XbetParser
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo
from fantasy_helper.db.dao.feature_store.fs_coeffs import FSCoeffsDAO


utc = timezone.utc


class CoeffDAO:
    TEAM1_MAX_LEN = 9
    TEAM2_MAX_LEN = 9

    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)

        self._xbet_parser = XbetParser(leagues=self._leagues)
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
        )

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
        current_tour = self._sports_parser.get_current_tour(league_name)
        if current_tour is not None and current_tour.number is not None:
            cur_tour_number = current_tour.number
        else:
            cur_tour_number = 0
        tour_number = cur_tour_number if tour == "cur" else cur_tour_number + 1

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

    def get_tour_number(self, league_name: str) -> Optional[int]:
        cur_tour = self._sports_parser.get_current_tour(league_name)
        if cur_tour is None:
            return None
        else:
            return cur_tour.number

    def update_coeffs(self, league_name: str) -> None:
        current_tour = self._sports_parser.get_current_tour(league_name)
        next_tour = self._sports_parser.get_next_tour(league_name)
        if current_tour is None or next_tour is None:
            return None
        matches = self._xbet_parser.get_league_matches(league_name)

        db_session: SQLSession = Session()

        for match in matches:
            if match.start_datetime < current_tour.deadline:
                match_tour = current_tour.number - 1
            elif match.start_datetime < next_tour.deadline:
                match_tour = current_tour.number
            else:
                match_tour = next_tour.number

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

    def update_feature_store(self) -> None:
        feature_store = FSCoeffsDAO()

        for league in self._leagues:
            cur_tour_matches = self.get_coeffs(league.name, "cur")
            next_tour_matches = self.get_coeffs(league.name, "next")
            feature_store.update_coeffs(league.name, "cur", cur_tour_matches)
            feature_store.update_coeffs(league.name, "next", next_tour_matches)
