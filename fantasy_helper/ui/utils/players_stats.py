from typing import Any, List, Optional, Union, get_args, get_origin
from dataclasses import asdict, dataclass, fields

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fantasy_helper.ui.utils.sports_players import rename_sports_role
from fantasy_helper.utils.dataclasses import PlayerStatsInfo, PlayersLeagueStats, PlayersStatsDiff


NOT_VISIBLE_COLUMNS = {"id", "type", "league_name", "name", "team", "position"}
COMMON_COLUMNS = {"sports_name", "sports_team", "role", "price", "games", "minutes"}
FREE_KICKS_COLUMNS = {"sports_name", "sports_team", "role", "price", "games", "penalty_shots", "corner_kicks", "free_kicks_shots"}
DEFAULT_COLUMNS = {"goals", "assists", "shots", "xg", "xg_xa"}

COLUMNS_NAMES = (
    ("sports_name", "Имя"),
    ("sports_team", "Команда"),
    ("role", "Позиция"),
    ("price", "Цена"),
    # sports popularity
    ("percent_ownership", "Популярность"),
    ("percent_ownership_diff", "Динамика"),
    # playing time
    ("games", "Матчи"),
    ("minutes", "Минуты"),
    # shooting
    ("goals", "Голы"),
    ("shots", "Удары"),
    ("shots_on_target", "УдСтвор"),
    ("average_shot_distance", "УдДист"),
    ("xg", "xG"),
    ("xg_np", "xGnp"),
    ("xg_xa", "xG + xA"),
    ("xg_np_xa", "xGnp + xAnp"),
    # passing
    ("assists", "ГолевыеПер"),
    ("xa", "xA"),
    ("key_passes", "КлючПасы"),
    ("passes_into_penalty_area", "ПасыПенЗон"),
    ("crosses_into_penalty_area", "ПасыШтрЗон"),
    # possesion
    ("touches_in_attacking_third", "КасФинТреть"),
    ("touches_in_attacking_penalty_area", "КасПенЗон"),
    ("carries_in_attacking_third", "КонтрФинТреть"),
    ("carries_in_attacking_penalty_area", "КонтрПенЗон"),
    # shot creation
    ("sca", "sca"),
    ("gca", "gca"),
    # standart shots
    ("corner_kicks", "Угловые"),
    ("penalty_goals", "ПенальтиЗаб"),
    ("penalty_shots", "Пенальти"),
    ("free_kicks_shots", "Штрафные"),
)
COLUMNS_MAPPING = {k: v for k, v in COLUMNS_NAMES}
COLUMNS_REVERSE_MAPPING = {v: k for k, v in COLUMNS_NAMES}


@st.cache_data(ttl=3600, max_entries=100, show_spinner="Loading players stats...")
def prepare_players_stats_df(
    players_stats: PlayersLeagueStats,
    games_count: int,
    is_abs_stats: bool = True,
    min_minutes: Optional[int] = None
) -> pd.DataFrame:
    if is_abs_stats:
        df = players_stats.abs_stats
    else:
        df = players_stats.norm_stats

    if df is None or len(df) == 0:
        return

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

    if not df.empty and "sports_name" in df.columns and "role" in df.columns:
        df = df.groupby(by=["name"]).apply(_get_max_game_count_row)
        df.drop(columns=NOT_VISIBLE_COLUMNS, inplace=True, errors="ignore")        
        df = df.loc[~df["sports_name"].isna()]
        df.reset_index(drop=True, inplace=True)
        df.fillna(0, inplace=True)
        df["role"] = df["role"].apply(rename_sports_role)

    return df


def plot_main_players_stats(
    players_stats_df: pd.DataFrame, 
    columns_names: List[str],
    team_name: str = "All",
    position: str = "All",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> None:
    """
    Plot the main players' stats based on the given parameters.

    Args:
        players_stats_df (pd.DataFrame): The DataFrame containing the players' stats.
        columns_names (List[str]): The names of the columns to plot.
        team_name (str, optional): The name of the team to filter the stats for. Defaults to "All".

    Returns:
        None
    """
    df_columns = players_stats_df.columns
    if team_name != "All" and "sports_team" in df_columns:
        players_stats_df = players_stats_df.loc[players_stats_df["sports_team"] == team_name]
    if position != "All" and "role" in df_columns:
        players_stats_df = players_stats_df.loc[players_stats_df["role"] == position]
    if min_price is not None and "price" in df_columns:
        players_stats_df = players_stats_df.loc[players_stats_df["price"] >= min_price]
    if max_price is not None and "price" in df_columns:
        players_stats_df = players_stats_df.loc[players_stats_df["price"] <= max_price]

    columns = []
    columns_names_set = set(COLUMNS_REVERSE_MAPPING.get(name) for name in columns_names)
    for column_key, column_name in COLUMNS_NAMES:
        if column_key in df_columns and \
            (column_key in COMMON_COLUMNS or column_key in columns_names_set):
            columns.append(column_key)

    players_stats_df = players_stats_df[columns].rename(columns=COLUMNS_MAPPING)
    st.dataframe(players_stats_df, hide_index=True)


def get_available_stats_columns(players_stats_df: pd.DataFrame) -> List[str]:
    result = []
    for column in list(players_stats_df.columns):
        if column not in COMMON_COLUMNS:
            column_name = COLUMNS_MAPPING.get(column)
            if column_name is not None:
                result.append(column_name)
    return result


def get_default_stats_columns(players_stats_df: pd.DataFrame) -> List[str]:
    result = []
    for column in list(players_stats_df.columns):
        if column not in COMMON_COLUMNS and column in DEFAULT_COLUMNS:
            column_name = COLUMNS_MAPPING.get(column)
            if column_name is not None:
                result.append(column_name)
    return result


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
    df.dropna(axis=1, how="all", inplace=True)
    df_columns = df.columns

    if team_name != "All" and "sports_team" in df_columns:
        df = df.loc[df["sports_team"] == team_name]
    if "sports_name" in df_columns:
        df = df.loc[~df["sports_name"].isna()]
    df.fillna(0, inplace=True)
    if "role" in df_columns:
        df["role"] = df["role"].apply(rename_sports_role)

    columns = []
    for column_name in df.columns:
        if column_name in FREE_KICKS_COLUMNS:
            columns.append(column_name)
    df = df[columns].rename(columns=COLUMNS_MAPPING)

    st.dataframe(df, hide_index=True)


def get_player_stats(
    players_stats_df: pd.DataFrame, 
    team_name: Optional[str], 
    name: Optional[str]
) -> Optional[PlayerStatsInfo]:
    if players_stats_df is None or len(players_stats_df) == 0 or \
        team_name is None or name is None:
        return

    df_columns = players_stats_df.columns
    if "sports_team" not in df_columns or "sports_name" not in df_columns:
        return None

    players_stats_df = players_stats_df.loc[players_stats_df["sports_team"] == team_name]

    for row_ind, row in players_stats_df.iterrows():
        if row["sports_name"] == name:
            return PlayerStatsInfo(**row)

    return None


def get_basic_type(optional_type: Any) -> Any:
    origin_type = get_origin(optional_type)
    if origin_type is not Optional and origin_type is not Union:
        return optional_type

    args = get_args(optional_type)
    if len(args) != 2 or args[1] is not type(None):
        return optional_type

    return args[0]


def compute_players_stats_diff(
    player_left: Optional[PlayerStatsInfo],
    player_right: Optional[PlayerStatsInfo],
    columns_names: List[str]
) -> PlayersStatsDiff:
    titles = []
    left_bars, right_bars = [], []
    left_abs_values, right_abs_values = [], []
    columns_names_set = set(columns_names)

    for field in fields(PlayerStatsInfo):
        left_value = getattr(player_left, field.name)
        right_value = getattr(player_right, field.name)

        if field.name not in COMMON_COLUMNS and field.name not in columns_names_set:
            continue

        if left_value is None or pd.isna(left_value) or \
            (not isinstance(left_value, int) and not isinstance(left_value, float)) \
            or right_value is None or pd.isna(left_value) or \
            (not isinstance(right_value, int) and not isinstance(right_value, float)):
            continue

        field_type = get_basic_type(field.type)
        left_value = field_type(left_value)
        right_value = field_type(right_value)

        titles.append(field.name)
        if left_value > right_value:
            if left_value > 0:
                left_bars.append(max(-(left_value - right_value) / left_value, -0.85))
            else:
                left_bars.append(0.0)
            right_bars.append(0.0)
            left_abs_values.append(left_value)
            right_abs_values.append(right_value)
        elif left_value < right_value:
            if right_value > 0:
                right_bars.append(min((right_value - left_value) / right_value, 0.85))
            else:
                right_bars.append(0.0)
            left_bars.append(0.0)
            left_abs_values.append(left_value)
            right_abs_values.append(right_value)
        else:
            left_bars.append(0.0)
            right_bars.append(0.0)
            left_abs_values.append(left_value)
            right_abs_values.append(right_value)

    titles.reverse()
    left_bars.reverse()
    right_bars.reverse()
    left_abs_values.reverse()
    right_abs_values.reverse()

    return PlayersStatsDiff(
        titles, 
        left_bars, 
        right_bars, 
        left_abs_values, 
        right_abs_values
    )


def plot_players_stats_diff(
    player_left: Optional[PlayerStatsInfo], 
    player_right: Optional[PlayerStatsInfo],
    columns_names: List[str]
) -> None:
    if player_left is None or player_right is None:
        return

    diff = compute_players_stats_diff(player_left, player_right, columns_names)

    fig = make_subplots(
        rows=1, 
        cols=2, 
        specs=[[{}, {}]], 
        shared_xaxes=True,
        shared_yaxes=True, 
        horizontal_spacing=0,
        subplot_titles=(player_left.name, player_right.name)
    )

    fig.append_trace(go.Bar(
        y=diff.titles,
        x=diff.left_bars, 
        text=diff.titles,
        textposition="none",
        orientation='h', 
        width=0.8, 
        showlegend=False, 
        marker_color='#4472c4',
        # name=player_left.name
    ), 1, 1)
    fig.append_trace(go.Bar(
        y=diff.titles,
        x=diff.right_bars, 
        text=diff.titles,
        textposition="none",
        orientation='h', 
        width=0.8, 
        showlegend=False, 
        marker_color='#ed7d31',
        # name=player_right.name
    ), 1, 2)

    for abs_value, diff_value, label in zip(diff.left_abs_values, diff.left_bars, diff.titles):
        fig.add_annotation(
            x=diff_value - 0.03,
            y=label,
            text=f"{abs_value:.2f}" if isinstance(abs_value, float) else str(abs_value),
            font=dict(family='Arial', size=12, color='#4472c4'),
            showarrow=False,
            row=1,
            col=1
        )
    for abs_value, diff_value, label in zip(diff.right_abs_values, diff.right_bars, diff.titles):
        fig.add_annotation(
            x=diff_value + 0.03,
            y=label,
            text=f"{abs_value:.2f}" if isinstance(abs_value, float) else str(abs_value),
            font=dict(family='Arial', size=12, color='#ed7d31'),
            showarrow=False,
            row=1,
            col=2
        )

    fig.update_yaxes(showticklabels=True, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_xaxes(showticklabels=False, range=[-1, 0], row=1, col=1)
    fig.update_xaxes(showticklabels=False, range=[0, 1], row=1, col=2)
 
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
