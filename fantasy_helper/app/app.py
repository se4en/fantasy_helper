from collections import defaultdict
from typing import List

import streamlit_authenticator as stauth
import pandas as pd
import streamlit as st
from fantasy_helper.db.dao.coeff import CoeffDAO

from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


Coeff_dao = CoeffDAO()


def get_stat_from_mathes(
    cur_tour_matches: List[MatchInfo], next_tour_matches: List[MatchInfo]
) -> dict:
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


def coeffs_to_df(league_name: str) -> pd.DataFrame:
    cur_tour_matches = Coeff_dao.get_coeffs(league_name, "cur")
    next_tour_matches = Coeff_dao.get_coeffs(league_name, "next")
    cur_tour_number = Coeff_dao.get_tour_number(league_name)

    team_stats = get_stat_from_mathes(cur_tour_matches, next_tour_matches)
    unique_teams = sorted(team_stats.keys())

    coeffs_info = defaultdict(list)
    for team_name in unique_teams:
        coeffs_info["Команда"].append(team_name)
        for tour_number, tour_type in enumerate(("cur", "next"), start=cur_tour_number):
            coeffs_info[f"Атака {tour_number} тур"].append(
                team_stats[team_name].get(f"{tour_type}_attack", None)
            )
            coeffs_info[f"Оборона {tour_number} тур"].append(
                team_stats[team_name].get(f"{tour_type}_defend", None)
            )
            coeffs_info[f"Соперник {tour_number} тур"].append(
                team_stats[team_name].get(f"{tour_type}_vs_name", None)
            )

    return pd.DataFrame(coeffs_info)


def highlight_survived(s):
    return (
        ["background-color: green"] * len(s)
        if s.Survived
        else ["background-color: red"] * len(s)
    )


def color_survived(val):
    if not isinstance(val, float):
        return ""
    elif val <= 1.5:
        color = "#85DE6F"
    elif val <= 2.0:
        color = "#EBE054"
    elif val <= 3.0:
        color = "#EBA654"
    else:
        color = "#E06456"

    return f"background-color: {color}"


df = coeffs_to_df("Russia")
coeffs_columns = list(
    filter(lambda x: x.startswith("Атака") or x.startswith("Оборона"), df.columns)
)
st.dataframe(df.style.applymap(color_survived, subset=coeffs_columns))
