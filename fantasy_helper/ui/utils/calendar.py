from collections import defaultdict
from typing import List, Literal

import numpy as np
import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import CalendarInfo


def update_calendar_info(
        calendar_info: dict, 
        team_name: str, 
        tour: int, 
        type: Literal["points", "xg"], 
        value: float,
        opponent_team: str
    ) -> None:
    if f"{tour}_{type}" not in calendar_info[team_name]:
        column_prefix = f"{tour}"
    else:
        column_prefix = f"{tour}_double"
    
    calendar_info[team_name][column_prefix + f"_{type}"] = value
    calendar_info[team_name][column_prefix + "_opponent"] = opponent_team

def get_calendar_df(calendar: List[CalendarInfo]) -> pd.DataFrame:
    calendar_info = defaultdict(lambda: defaultdict(list))
    tours = set()

    for calendar_row in sorted(calendar, key=lambda x: x.tour):
        tour = calendar_row.tour
        tours.add(tour)

        update_calendar_info(
            calendar_info, 
            calendar_row.home_team, 
            tour, 
            "points", 
            calendar_row.home_points_score,
            calendar_row.away_team + " [д]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.home_team, 
            tour, 
            "xg", 
            calendar_row.home_xg_score,
            calendar_row.away_team + " [д]",
        )

        update_calendar_info(
            calendar_info, 
            calendar_row.away_team, 
            tour, 
            "points", 
            calendar_row.away_points_score,
            calendar_row.home_team + " [г]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.away_team, 
            tour, 
            "xg", 
            calendar_row.away_xg_score,
            calendar_row.home_team + " [г]",
        )

    result = defaultdict(list)
    unique_teams = set([row.home_team for row in calendar] + [row.away_team for row in calendar])
    for team_name in sorted(unique_teams):
        result["team"].append(team_name)
        for tour in sorted(tours):
            for type in ["points", "xg", "opponent"]:
                result[f"{tour}_{type}"].append(
                    calendar_info.get(team_name, {}).get(f"{tour}_{type}")
                )
                result[f"{tour}_double_{type}"].append(
                    calendar_info.get(team_name, {}).get(f"{tour}_double_{type}")
                )

    return pd.DataFrame(result)


def rename_column(column_name: str) -> str:
    if column_name == "team":
        return "Команда"
    else: 
        result = column_name.replace("_points", "").replace("_xg", "").replace("_double", "")
        result += " тур"
        if "double" in column_name:
            result += " доп"

        return result


def color_value(
    val: float, q_1: float, q_2: float, q_3: float, q_4: float
) -> str:
    if pd.isna(val):
        return ""
    elif val <= q_1:
        color = "#E06456"
    elif val <= q_2:
        color = "#EBA654" # "#E57878"
    elif val > q_4:
        color = "#85DE6F"
    elif val > q_3:
        color = "#EBE054" # "#85DE6F"
    else:
        return ""

    return f"background-color: {color}"

def color_df(df):
    df_with_colors = pd.DataFrame('', index=df.index, columns=df.columns)
    for column_name in df.columns:
        if column_name != "team" and not column_name.endswith("_opponent"):
            column_prefix = "_".join(column_name.split("_")[:-1])
            opponent_column_name = f"{column_prefix}_opponent"

            # TODO: remove it to backend
            q1 = np.percentile(df[column_name], q=25)
            q2 = np.percentile(df[column_name], q=50)
            q3 = np.percentile(df[column_name], q=75)

            df_with_colors[opponent_column_name] = df[column_name].copy().map(
                lambda x: color_value(x, q1, q2, q2, q3)
            )

    return df_with_colors


def plot_calendar_df(df: pd.DataFrame, type: Literal["points", "xg"]) -> None:
    df = df.dropna(how='all', axis=1, inplace=False)

    valid_columns, hide_columns_idxs = [], []
    for colimn_idx, column_name in enumerate(df.columns):
        if column_name == "team" or column_name.endswith(f"_{type}"):
            valid_columns.append(column_name)
        else:
            hide_columns_idxs.append(colimn_idx)

    st.dataframe(
        df.style.apply(color_df, axis=None)
        # .hide(hide_columns_idxs).relabel_index(valid_columns)
    )
