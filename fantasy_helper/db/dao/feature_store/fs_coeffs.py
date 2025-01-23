from typing import List, Literal

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.feature_store.fs_coeffs import FSCoeffs
from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import MatchInfo


class FSCoeffsDAO:
    def get_coeffs(
        self, league_name: str) -> List[MatchInfo]:
        db_session: SQLSession = Session()

        cur_tour_matches = (
            db_session.query(FSCoeffs)
            .filter(FSCoeffs.league_name == league_name)
            .all()
        )

        result = [
            MatchInfo(
                url=match.url,
                league_name=match.league_name,
                home_team=match.home_team,
                away_team=match.away_team,
                start_datetime=match.start_datetime,
                tour_number=match.tour_number,
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

    def update_coeffs(
        self, league_name: str, matches: List[MatchInfo]
    ) -> None:
        db_session: SQLSession = Session()

        # remove all previous matches
        db_session.query(FSCoeffs).filter(
            FSCoeffs.league_name == league_name
        ).delete()

        # add new matches
        for match in matches:
            db_session.add(
                FSCoeffs(
                    home_team=match.home_team,
                    away_team=match.away_team,
                    league_name=league_name,
                    start_datetime=match.start_datetime,
                    tour_number=match.tour_number,
                    url=match.url,
                    total_1_over_1_5=match.total_1_over_1_5,
                    total_2_over_1_5=match.total_2_over_1_5,
                    total_1_under_0_5=match.total_1_under_0_5,
                    total_2_under_0_5=match.total_2_under_0_5,
                )
            )

        db_session.commit()
        db_session.close()
