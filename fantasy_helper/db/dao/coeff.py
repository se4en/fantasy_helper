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
from fantasy_helper.db.dao.feature_store.fs_coeffs import FSCoeffsDAO
from fantasy_helper.db.dao.ml.naming import NamingDAO
from fantasy_helper.parsers.xbet import XbetParser
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


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
        self._naming_dao = NamingDAO()

    def get_actual_coeffs(self, league_name: str) -> List[MatchInfo]:
        current_datetime = datetime.now()

        db_session: SQLSession = Session()

        actual_coeffs_rows = (
            db_session.query(Coeff)
            .filter(and_(
                Coeff.league_name == league_name, 
                Coeff.start_datetime >= current_datetime
            ))
            .subquery()
        )

        actual_coeffs_matches = db_session.query(
            actual_coeffs_rows,
            func.rank()
            .over(
                order_by=actual_coeffs_rows.c.timestamp.desc(),
                partition_by=(actual_coeffs_rows.c.home_team, actual_coeffs_rows.c.away_team),
            )
            .label("rnk"),
        ).subquery()

        actual_coeffs = (
            db_session.query(actual_coeffs_matches)
            .filter(actual_coeffs_matches.c.rnk == 1)
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
            for match in actual_coeffs
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
        matches = self._xbet_parser.get_league_matches(league_name)

        db_session: SQLSession = Session()

        for match in matches:
            db_session.add(
                Coeff(
                    **match.__dict__,
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
            actual_coeffs = self.get_actual_coeffs(league.name)
            sports_matches = self._sports_parser.get_next_matches(
                league.name, 2
            )
            sports_coeffs = self._naming_dao.add_sports_info_to_coeffs(
                league.name, actual_coeffs, sports_matches
            )
            feature_store.update_coeffs(league.name, sports_coeffs)
