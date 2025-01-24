from collections import defaultdict
from typing import List

import pandas as pd
import streamlit as st

from fantasy_helper.utils.dataclasses import MatchInfo


def get_unique_teams(matches: List[MatchInfo]) -> List[str]:
    unique_teams = set(
        [match.home_team for match in matches] + [match.away_team for match in matches]
    )
    return sorted(unique_teams)


def get_coeffs_info_from_mathes(matches: List[MatchInfo], unique_teams: List[str]) -> dict:
    team_2_matches = dict()
    for team_name in unique_teams:
        team_2_matches[team_name] = dict()

    unique_tours = set()
    for match in matches:
        if str(match.tour_number) in match.home_team:
            home_tour_name = str(match.tour_number) + " тур доп"
        else:
            home_tour_name = str(match.tour_number) + " тур"
        team_2_matches[match.home_team][home_tour_name] = match
        unique_tours.add(home_tour_name)

        if str(match.tour_number) in match.away_team:
            away_tour_name = str(match.tour_number) + " тур доп"
        else:
            away_tour_name = str(match.tour_number) + " тур"
        team_2_matches[match.away_team][away_tour_name] = match
        unique_tours.add(away_tour_name)
    unique_tours = sorted(unique_tours)

    coeffs_info = defaultdict(list)
    for team_name, matches in team_2_matches.items():
        coeffs_info["Команда"].append(team_name)
        for tour_name in unique_tours:
            if tour_name in matches:
                tour_match = matches[tour_name]
                if team_name == tour_match.home_team:
                    coeffs_info[f"Атака {tour_name}"].append(
                        tour_match.total_1_over_1_5
                    )
                    coeffs_info[f"Защита {tour_name}"].append(
                        tour_match.total_2_under_0_5
                    )
                    coeffs_info[f"Соперник {tour_name}"].append(
                        tour_match.away_team + " [д]"
                    )
                else:
                    coeffs_info[f"Атака {tour_name}"].append(
                        tour_match.total_2_over_1_5
                    )
                    coeffs_info[f"Защита {tour_name}"].append(
                        tour_match.total_1_under_0_5
                    )
                    coeffs_info[f"Соперник {tour_name}"].append(
                        tour_match.home_team + " [г]"
                    )
            else:
                coeffs_info[f"Атака {tour_name}"].append(None)
                coeffs_info[f"Защита {tour_name}"].append(None)
                coeffs_info[f"Соперник {tour_name}"].append(None)

    return coeffs_info


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
        .map(lambda x: color_coeff(x, 2.0, 2.5, 3.5), subset=defend_columns),
        hide_index=True
    )
