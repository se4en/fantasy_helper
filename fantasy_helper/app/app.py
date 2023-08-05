from collections import defaultdict
from typing import List

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


if not GlobalHydra().is_initialized():
    initialize(config_path="../conf", version_base=None)
cfg = compose(config_name="config")
leagues = {league.ru_name: league.name for league in instantiate(cfg.leagues)}
credentials = instantiate(cfg.credentials)
cookie = instantiate(cfg.cookie)

authenticator = stauth.Authenticate(credentials, **cookie)
name, authentication_status, username = authenticator.login("Login", "main")

Coeff_dao = CoeffDAO()

st.session_state["league"] = list(leagues.keys())[0]


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
            coeffs_info[f"Защита {tour_number} тур"].append(
                team_stats[team_name].get(f"{tour_type}_defend", None)
            )
            coeffs_info[f"Соперник {tour_number} тур"].append(
                team_stats[team_name].get(f"{tour_type}_vs_name", None)
            )

    return pd.DataFrame(coeffs_info)


def color_coeff(
    val: float, th_0: float = 1.5, th_1: float = 2.0, th_2: float = 3.0
) -> str:
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
    not_na_columns = df.columns[~df.isna().all()]
    attack_columns = list(filter(lambda x: x.startswith("Атака"), not_na_columns))
    defend_columns = list(filter(lambda x: x.startswith("Защита"), not_na_columns))

    st.dataframe(
        df.style.format("{:.3}", subset=attack_columns + defend_columns)
        .applymap(color_coeff, subset=attack_columns)
        .applymap(lambda x: color_coeff(x, 2.0, 2.5, 3.5), subset=defend_columns)
    )


if authentication_status:
    st.session_state["league"] = leagues[
        st.selectbox("League", sorted(leagues.keys()), label_visibility="collapsed")
    ]
    df = coeffs_to_df(st.session_state["league"])
    plot_coeff_df(df)
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
