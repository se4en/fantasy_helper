from typing import List, Optional

import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import PlayersLeagueStats


NOT_VISIBLE_COLUMNS = {"id", "type", "league_name"}
DEFAULT_COLUMNS = {"name", "team", "position", "games", "minutes"}


def plot_main_players_stats(
    players_stats: PlayersLeagueStats,
    games_count: int,
    is_abs_stats: bool = True,
    min_minutes: Optional[int] = None,
    team_name: str = "All",
) -> None:
    """
    Plot the main players' stats based on the given parameters.

    Args:
        players_stats (PlayersLeagueStats): The object containing the players' league stats.
        games_count (int): The maximum number of games to consider.
        is_abs_stats (bool, optional): Flag indicating whether to use absolute stats or normalized stats. Defaults to True.
        min_minutes (Optional[int], optional): The minimum number of minutes played to consider. Defaults to None.
        team_name (str, optional): The name of the team to filter the stats for. Defaults to "All".

    Returns:
        None
    """
    if is_abs_stats:
        df = players_stats.abs_stats
    else:
        df = players_stats.norm_stats

    if df is None or len(df) == 0:
        return

    df.drop(columns=NOT_VISIBLE_COLUMNS, inplace=True, errors="ignore")

    if team_name != "All":
        df = df.loc[df["team"] == team_name]
    df = df.loc[df["games"] <= games_count]
    if min_minutes is not None:
        df = df.loc[df["minutes"] >= min_minutes]

    df.dropna(axis=1, how="all", inplace=True)

    def _get_max_game_count_row(group: pd.DataFrame) -> pd.DataFrame:
        """
        Get the row with the maximum game count from a given group.

        Args:
            group (pd.DataFrame): The group of data to search for the row with the maximum game count.

        Returns:
            pd.DataFrame: The row with the maximum game count, as a DataFrame. If no such row exists, an empty DataFrame is returned.
        """
        result = group.loc[group["games"] == group["games"].max()]
        if len(result) > 0:
            return pd.DataFrame(result.iloc[0].to_dict(), index=[0])
        else:
            return pd.DataFrame()

    if not df.empty:
        df = df.groupby(by=["name"]).apply(_get_max_game_count_row)
        df.reset_index(drop=True, inplace=True)
        df.fillna(0, inplace=True)

    st.dataframe(df, hide_index=True)


def get_all_stats_columns(df: pd.DataFrame) -> List[str]:
    pass


def get_default_stats_columns(df: pd.DataFrame) -> List[str]:
    pass


def plot_free_kicks_stats(
    players_stats: PlayersLeagueStats, team_name: str = "All"
) -> None:
    """
    Generate a plot of free kicks statistics for players.

    Args:
        players_stats (PlayersLeagueStats): The players' league statistics.
        team_name (str, optional): The name of the team to filter the statistics for. Defaults to "All".

    Returns:
        None

    """
    df = players_stats.free_kicks

    if df is None or len(df) == 0:
        return

    df.drop(columns=NOT_VISIBLE_COLUMNS, inplace=True, errors="ignore")

    if team_name != "All":
        df = df.loc[df["team"] == team_name]
    df.dropna(axis=1, how="all", inplace=True)
    df.fillna(0, inplace=True)

    st.dataframe(df, hide_index=True)
