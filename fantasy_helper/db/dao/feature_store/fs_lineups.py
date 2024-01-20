from typing import List

from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.lineup import Lineup
from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import TeamLineup
from fantasy_helper.db.models.feature_store.fs_lineups import FSLineups


class FSLineupsDAO:
    def get_lineups(self, league_name: str) -> List[TeamLineup]:
        """
        Retrieves the lineups for a given league.

        Parameters:
            league_name (str): The name of the league.

        Returns:
            List[TeamLineup]: A list of `TeamLineup` objects representing the lineups for the league.
        """
        db_session: SQLSession = Session()

        league_lineups = (
            db_session.query(FSLineups).filter(Lineup.league_name == league_name).all()
        )

        result = [
            TeamLineup(
                team_name=lineup.team_name,
                league_name=lineup.league_name,
                lineup=lineup.lineup,
            )
            for lineup in league_lineups
        ]

        db_session.commit()
        db_session.close()

        return result

    def update_lineups(self, league_name: str, lineups: List[TeamLineup]) -> None:
        """
        Update the lineups for a given league.

        Args:
            league_name (str): The name of the league.
            lineups (List[TeamLineup]): A list of TeamLineup objects representing the new lineups.

        Returns:
            None
        """
        db_session: SQLSession = Session()

        # remove all previous matches
        db_session.query(FSLineups).filter(
            FSLineups.league_name == league_name
        ).delete()

        # add new lineups
        for lineup in lineups:
            db_session.add(
                FSLineups(
                    league_name=lineup.league_name,
                    team_name=lineup.team_name,
                    lineup=lineup.lineup,
                )
            )

        db_session.commit()
        db_session.close()
