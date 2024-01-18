from typing import List, Literal

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.feature_store.fs_coeffs import FSCoeff
from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import MatchInfo


class FSCoeffsDAO:
    def get_coeffs(
        self, league_name: str, tour: Literal["cur", "next"]
    ) -> List[MatchInfo]:
        """
        Retrieves the coefficients for a given league and tour.

        Args:
            league_name (str): The name of the league.
            tour (Literal["cur", "next"]): The tour, either "cur" for the current tour or "next" for the next tour.

        Returns:
            List[MatchInfo]: A list of MatchInfo objects representing the coefficients for the given league and tour.
        """
        db_session: SQLSession = Session()

        cur_tour_matches = (
            db_session.query(FSCoeff)
            .filter(and_(FSCoeff.league_name == league_name, FSCoeff.tour == tour))
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

    def update_coeffs(
        self, league_name: str, tour: Literal["cur", "next"], matches: List[MatchInfo]
    ) -> None:
        """
        Update the coefficients for a given league and tour with new matches.

        Args:
            league_name (str): The name of the league.
            tour (Literal["cur", "next"]): The tour to update the coefficients for.
            matches (List[MatchInfo]): The list of new matches.

        Returns:
            None: This function does not return anything.
        """
        db_session: SQLSession = Session()

        # remove all previous matches
        db_session.query(FSCoeff).filter(
            and_(FSCoeff.league_name == league_name, FSCoeff.tour == tour)
        ).delete()

        # add new matches
        for match in matches:
            db_session.add(
                FSCoeff(
                    home_team=match.home_team,
                    away_team=match.away_team,
                    league_name=league_name,
                    tour=tour,
                    start_datetime=match.start_datetime,
                    url=match.url,
                    total_1_over_1_5=match.total_1_over_1_5,
                    total_2_over_1_5=match.total_2_over_1_5,
                    total_1_under_0_5=match.total_1_under_0_5,
                    total_2_under_0_5=match.total_2_under_0_5,
                )
            )

        db_session.commit()
        db_session.close()
