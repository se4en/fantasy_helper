from collections import defaultdict
from typing import List, Literal, Optional

import numpy as np
import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import CalendarInfo


def update_calendar_info(
        calendar_info: dict, 
        team_name: str, 
        tour: int, 
        type: Literal["points", "goals", "xg"], 
        color: str,
        opponent_team: str
    ) -> None:
    if f"{tour}_{type}" not in calendar_info[team_name]:
        column_prefix = f"{tour}"
    else:
        column_prefix = f"{tour}_double"
    
    calendar_info[team_name][column_prefix + f"_{type}"] = color
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
            calendar_row.home_points_color,
            calendar_row.away_team + " [д]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.home_team, 
            tour, 
            "goals", 
            calendar_row.home_goals_color,
            calendar_row.away_team + " [д]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.home_team, 
            tour, 
            "xg", 
            calendar_row.home_xg_color,
            calendar_row.away_team + " [д]",
        )

        update_calendar_info(
            calendar_info, 
            calendar_row.away_team, 
            tour, 
            "points", 
            calendar_row.away_points_color,
            calendar_row.home_team + " [г]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.away_team, 
            tour, 
            "goals", 
            calendar_row.away_goals_color,
            calendar_row.home_team + " [г]",
        )
        update_calendar_info(
            calendar_info, 
            calendar_row.away_team, 
            tour, 
            "xg", 
            calendar_row.away_xg_color,
            calendar_row.home_team + " [г]",
        )

    result = defaultdict(list)
    unique_teams = set([row.home_team for row in calendar] + [row.away_team for row in calendar])
    for team_name in sorted(unique_teams):
        result["team"].append(team_name)
        for tour in sorted(tours):
            for type in ["points", "goals", "xg", "opponent"]:
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
        result = column_name.replace("_points", "").replace("_goals", "") \
            .replace("_xg", "").replace("_double", "")
        result += " тур"
        if "double" in column_name:
            result += " доп"

        return result
    

def format_color(color: Optional[str]) -> str:
    if color is None or pd.isna(color) or color == "":
        return ""
    else:
        return f"background-color: {color}"


def color_df(df, type: Literal["points", "goals", "xg"]):
    df_with_colors = pd.DataFrame('', index=df.index, columns=df.columns)
    for column_name in df.columns:
        if column_name.endswith(f"_{type}"):
            column_prefix = "_".join(column_name.split("_")[:-1])
            opponent_column_name = f"{column_prefix}_opponent"
            df_with_colors[opponent_column_name] = df[column_name].copy().map(format_color)

    return df_with_colors


def plot_calendar_df(df: pd.DataFrame, type: Literal["points", "goals", "xg"]) -> None:
    df = df.dropna(how='all', axis=1, inplace=False)
    df.fillna("", inplace=True)

    column_config = {}
    for column_name in list(df.columns):
        if column_name != "team" and not column_name.endswith(f"_opponent"):
            column_config[column_name] = None
        else:
            column_config[column_name] = rename_column(column_name)

    st.dataframe(
        df.style.apply(lambda x: color_df(x, type), axis=None),
        column_config=column_config
    )
