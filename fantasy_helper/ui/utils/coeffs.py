from typing import List

import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import MatchInfo


def get_stat_from_mathes(
    cur_tour_matches: List[MatchInfo], next_tour_matches: List[MatchInfo]
) -> dict:
    """
    Generate a dictionary containing statistical information for each team based on the given lists of current tour matches and next tour matches.

    Args:
        cur_tour_matches (List[MatchInfo]): A list of MatchInfo objects representing the matches in the current tour.
        next_tour_matches (List[MatchInfo]): A list of MatchInfo objects representing the matches in the next tour.

    Returns:
        dict: A dictionary with team names as keys and nested dictionaries as values. Each nested dictionary contains statistical information for the corresponding team, including the opponent's name in the current and next tour, attack and defense statistics for the current tour, and attack and defense statistics for the next tour.
    """
    unique_teams = set(
        [match.home_team for match in cur_tour_matches + next_tour_matches]
        + [match.away_team for match in cur_tour_matches + next_tour_matches]
    )
    result = {team_name: {} for team_name in unique_teams}

    for matches, tour_type in zip(
        (cur_tour_matches, next_tour_matches), ("cur", "next")
    ):
        for match in matches:
            result[match.home_team][f"{tour_type}_vs_name"] = match.away_team + " [д]"
            # result[match.home_team][f"{tour_type}_vs_loc"] = ""
            result[match.home_team][f"{tour_type}_attack"] = match.total_1_over_1_5
            result[match.home_team][f"{tour_type}_defend"] = match.total_2_under_0_5

            result[match.away_team][f"{tour_type}_vs_name"] = match.home_team + " [г]"
            # result[match.away_team][f"{tour_type}_vs_loc"] = "away"
            result[match.away_team][f"{tour_type}_attack"] = match.total_2_over_1_5
            result[match.away_team][f"{tour_type}_defend"] = match.total_1_under_0_5

    return result


def color_coeff(
    val: float, th_0: float = 1.5, th_1: float = 2.0, th_2: float = 3.0
) -> str:
    """
    Calculate the color coefficient based on the input value.

    Args:
        val (float): The input value.
        th_0 (float, optional): The threshold for color category 0. Defaults to 1.5.
        th_1 (float, optional): The threshold for color category 1. Defaults to 2.0.
        th_2 (float, optional): The threshold for color category 2. Defaults to 3.0.

    Returns:
        str: The CSS background color based on the input value.
    """
    if pd.isna(val):
        return ""
    elif val <= th_0:
        color = "#85DE6F"
    elif val <= th_1:
        color = "#EBE054"
    elif val <= th_2:
        color = "#EBA654"
    else:
        color = "#E06456"

    return f"background-color: {color}"


def plot_coeff_df(df: pd.DataFrame):
    """
    Plot the coefficient dataframe.

    Args:
        df (pd.DataFrame): The dataframe containing the coefficient data.

    Returns:
        None
    """
    not_na_columns = df.columns[~df.isna().all()]
    attack_columns = list(filter(lambda x: x.startswith("Атака"), not_na_columns))
    defend_columns = list(filter(lambda x: x.startswith("Защита"), not_na_columns))

    st.dataframe(
        df.style.format("{:.3}", subset=attack_columns + defend_columns)
        .map(color_coeff, subset=attack_columns)
        .map(lambda x: color_coeff(x, 2.0, 2.5, 3.5), subset=defend_columns)
    )
