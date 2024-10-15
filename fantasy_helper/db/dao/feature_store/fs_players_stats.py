import numpy as np
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import PlayersLeagueStats
from fantasy_helper.db.models.feature_store.fs_players_free_kicks import (
    FSPlayersFreeKicks,
)
from fantasy_helper.db.models.feature_store.fs_players_stats import FSPlayersStats


class FSPlayersStatsDAO:
    def get_players_stats(self, league_name: str) -> PlayersLeagueStats:
        """
        Retrieves the player statistics for a given league.

        Args:
            league_name (str): The name of the league.

        Returns:
            PlayersLeagueStats: An object containing the player statistics for the league. The object has the following attributes:
                - abs_stats (pandas.DataFrame): A DataFrame containing the absolute player statistics.
                - norm_stats (pandas.DataFrame): A DataFrame containing the normalized player statistics.
                - free_kicks (pandas.DataFrame): A DataFrame containing the player free kick statistics.
        """
        db_session: SQLSession = Session()

        abs_players_stats = db_session.query(FSPlayersStats).filter(
            and_(
                FSPlayersStats.league_name == league_name,
                FSPlayersStats.type == "abs",
            )
        )

        norm_players_stats = db_session.query(FSPlayersStats).filter(
            and_(
                FSPlayersStats.league_name == league_name,
                FSPlayersStats.type == "norm",
            )
        )

        players_free_kicks = db_session.query(FSPlayersFreeKicks).filter(
            FSPlayersFreeKicks.league_name == league_name
        )

        abs_players_stats_df = pd.read_sql(
            abs_players_stats.statement, abs_players_stats.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        norm_players_stats_df = pd.read_sql(
            norm_players_stats.statement, norm_players_stats.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        players_free_kicks_df = pd.read_sql(
            players_free_kicks.statement, players_free_kicks.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        db_session.commit()
        db_session.close()

        result = PlayersLeagueStats(
            abs_stats=abs_players_stats_df,
            norm_stats=norm_players_stats_df,
            free_kicks=players_free_kicks_df,
        )

        return result

    def update_players_stats(
        self, league_name: str, players_stats: PlayersLeagueStats
    ) -> None:
        """
        Updates the player statistics for a given league.

        Args:
            league_name (str): The name of the league.
            players_stats (PlayersLeagueStats): The player statistics to update.

        Returns:
            None: This function does not return anything.
        """
        db_session: SQLSession = Session()

        # remove all previous stats
        db_session.query(FSPlayersStats).filter(
            FSPlayersStats.league_name == league_name
        ).delete()

        # add new stats
        for index, abs_player_stats in players_stats.abs_stats.replace(
            np.nan, None
        ).iterrows():
            db_session.add(
                FSPlayersStats(type="abs", league_name=league_name, **abs_player_stats)
            )

        for index, norm_player_stats in players_stats.norm_stats.replace(
            np.nan, None
        ).iterrows():
            db_session.add(
                FSPlayersStats(
                    type="norm", league_name=league_name, **norm_player_stats
                )
            )

        # remove all previous stats
        db_session.query(FSPlayersFreeKicks).filter(
            FSPlayersFreeKicks.league_name == league_name
        ).delete()

        for index, free_kick_stats in players_stats.free_kicks.replace(
            np.nan, None
        ).iterrows():
            db_session.add(
                FSPlayersFreeKicks(league_name=league_name, **free_kick_stats)
            )

        db_session.commit()
        db_session.close()
