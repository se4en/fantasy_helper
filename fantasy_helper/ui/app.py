from collections import defaultdict
from typing import List

import requests
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from hydra.utils import instantiate

from fantasy_helper.ui.utils import (
    color_coeff,
    get_stat_from_mathes,
    lineup_to_formation,
    plot_lineup,
)
from fantasy_helper.utils.common import load_config
from fantasy_helper.utils.dataclasses import PlayersLeagueStats


api_url = "http://api:80"
cfg = load_config(config_path="../conf", config_name="config")

# streamlit utils
credentials = instantiate(cfg.credentials)
cookie = instantiate(cfg.cookie)

# streamlit options
st.set_page_config(
    page_title="Fantasy Helper",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.write("credentials")
st.write(credentials)

authenticator = stauth.Authenticate(credentials, **cookie)
# authenticator = stauth.Authenticate(credentials)
name, authentication_status, username = authenticator.login("Login", "main")

st.write("Res")
st.write(name, authentication_status, username)


# @st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading coefficients...")
# def coeffs_to_df(league_name: str) -> pd.DataFrame:
#     cur_tour_r = requests.get(
#         api_url + "/coeffs", data={"league_name": league_name, "tour": "cur"}
#     )
#     next_tour_r = requests.get(
#         api_url + "/coeffs", data={"league_name": league_name, "tour": "next"}
#     )
#     cur_tour_number_r = requests.get(
#         api_url + "/tour_number", data={"league_name": league_name}
#     )

#     cur_tour_matches = cur_tour_r.json()
#     next_tour_matches = next_tour_r.json()
#     cur_tour_number = cur_tour_number_r.json()

#     team_stats = get_stat_from_mathes(cur_tour_matches, next_tour_matches)
#     unique_teams = sorted(team_stats.keys())

#     coeffs_info = defaultdict(list)
#     for team_name in unique_teams:
#         coeffs_info["Команда"].append(team_name)
#         for tour_number, tour_type in enumerate(("cur", "next"), start=cur_tour_number):
#             coeffs_info[f"Атака {tour_number} тур"].append(
#                 team_stats[team_name].get(f"{tour_type}_attack", None)
#             )
#             coeffs_info[f"Защита {tour_number} тур"].append(
#                 team_stats[team_name].get(f"{tour_type}_defend", None)
#             )
#             coeffs_info[f"Соперник {tour_number} тур"].append(
#                 team_stats[team_name].get(f"{tour_type}_vs_name", None)
#             )

#     return pd.DataFrame(coeffs_info)


# @st.cache_data(ttl=3600, max_entries=500, show_spinner="Loading players stats...")
# def get_players_league_stats(league_name: str) -> PlayersLeagueStats:
#     r = requests.get(api_url + "/players_stats", data={"league_name": league_name})
#     league_stats = PlayersLeagueStats()
#     league_stats.from_json(r.json())

#     return league_stats


# @st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading teams...")
# def get_teams_names(league_name: str):
#     r = requests.get(
#         api_url + "/players_teams_names", data={"league_name": league_name}
#     )
#     return r.json()


# @st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading lineups...")
# def get_lineups(league_name: str):
#     r = requests.get(api_url + "/lineups", data={"league_name": league_name})
#     return r.json()


# @st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading lineups...")
# def get_leagues():
#     r = requests.get(api_url + "/leagues_names")
#     return r.json()


# def plot_coeff_df(df: pd.DataFrame):
#     not_na_columns = df.columns[~df.isna().all()]
#     attack_columns = list(filter(lambda x: x.startswith("Атака"), not_na_columns))
#     defend_columns = list(filter(lambda x: x.startswith("Защита"), not_na_columns))

#     st.dataframe(
#         df.style.format("{:.3}", subset=attack_columns + defend_columns)
#         .map(color_coeff, subset=attack_columns)
#         .map(lambda x: color_coeff(x, 2.0, 2.5, 3.5), subset=defend_columns)
#     )


# def plot_main_players_stats(
#     players_stats: PlayersLeagueStats,
#     games_count: int,
#     is_abs_stats: bool = True,
#     min_minutes: int = 5,
#     team_name: str = "All",
# ) -> None:
#     if is_abs_stats:
#         df = players_stats.abs_stats
#     else:
#         df = players_stats.norm_stats

#     if df is None or len(df) == 0:
#         return

#     if team_name != "All":
#         df = df.loc[df["team"] == team_name]
#     df = df.loc[df["games"] <= games_count]
#     df = df.loc[df["minutes"] >= min_minutes]
#     df.dropna(axis=1, how="all", inplace=True)

#     def _get_max_game_count_row(group: pd.DataFrame) -> pd.DataFrame:
#         result = group.loc[group["games"] == group["games"].max()]
#         if len(result) > 0:
#             return pd.DataFrame(result.iloc[0].to_dict(), index=[0])
#         else:
#             return pd.DataFrame()

#     df = df.groupby(by=["name"]).apply(_get_max_game_count_row)
#     df.reset_index(drop=True, inplace=True)
#     df.fillna(0, inplace=True)

#     st.dataframe(df)


# def plot_free_kicks_stats(
#     players_stats: PlayersLeagueStats, team_name: str = "All"
# ) -> None:
#     df = players_stats.free_kicks

#     if df is None or len(df) == 0:
#         return

#     if team_name != "All":
#         df = df.loc[df["team"] == team_name]
#     df.dropna(axis=1, how="all", inplace=True)
#     df.fillna(0, inplace=True)

#     st.dataframe(df)


# def centrize_header(text: str):
#     style = "<style>h2 {text-align: center;}</style>"
#     st.markdown(style, unsafe_allow_html=True)
#     st.header(text)


# leagues = get_leagues()
# st.session_state["league"] = list(leagues.values())[0]
# st.session_state["normalize"] = False
# st.session_state["games_count"] = 3
# st.session_state["min_minutes"] = 5

if authentication_status:
    # leagues = get_leagues()
    # st.session_state["league"] = list(leagues.values())[0]
    # st.session_state["normalize"] = False
    # st.session_state["games_count"] = 3
    # st.session_state["min_minutes"] = 5

    # with st.columns(3)[1]:
    #     centrize_header("League name")
    #     st.session_state["league"] = leagues[
    #         st.selectbox(
    #             "League name", sorted(leagues.keys()), label_visibility="collapsed"
    #         )
    #     ]
    # st.write("")

    # players_league_stats = get_players_league_stats(st.session_state["league"])
    # coeffs_df = coeffs_to_df(st.session_state["league"])
    # team_names = get_teams_names(st.session_state["league"])
    # lineups = get_lineups(st.session_state["league"])

    # left, right = st.columns([4, 2])
    # # plot coeffs
    # with left:
    #     centrize_header("Coefficients")
    #     plot_coeff_df(coeffs_df)

    # # plot lineup
    # with right:
    #     centrize_header("Lineups")
    #     lineups = {lineup.team_name: lineup.lineup for lineup in lineups}
    #     team_name = st.selectbox(
    #         "Team", sorted(list(lineups.keys())), label_visibility="visible"
    #     )
    #     if team_name is not None:
    #         formation, positions, names = lineup_to_formation(lineups[team_name])
    #         if len(positions) == 11 and len(names) == 11:
    #             fig = plot_lineup(formation, positions, names)
    #             st.pyplot(fig=fig, clear_figure=None, use_container_width=True)
    #         else:
    #             st.write(lineups[team_name])

    # # plot stats
    # centrize_header("Players stats")

    # columns = st.columns([2, 2, 2, 2])
    # with columns[0]:
    #     st.selectbox(
    #         "Team name",
    #         options=["All"] + team_names,
    #         key="player_stats_team_name",
    #         label_visibility="visible",
    #     )
    # with columns[1]:
    #     st.session_state["games_count"] = st.number_input(
    #         "Games count", value=3, min_value=1, max_value=30, step=1
    #     )
    # with columns[2]:
    #     st.session_state["min_minutes"] = st.number_input(
    #         "Minimum minutes", value=10, min_value=1, max_value=1000, step=1
    #     )
    # with columns[3]:
    #     st.write("")
    #     st.write("")
    #     st.session_state["normalize"] = st.toggle("Normalize per 90 minutes")

    # plot_main_players_stats(
    #     players_league_stats,
    #     games_count=st.session_state["games_count"],
    #     is_abs_stats=not st.session_state["normalize"],
    #     min_minutes=st.session_state["min_minutes"],
    #     team_name=st.session_state["player_stats_team_name"],
    # )

    # # plot free kicks stats
    # centrize_header("Free kicks stats")

    # columns = st.columns([2, 2, 2])
    # with columns[1]:
    #     st.selectbox(
    #         "Team name",
    #         options=["All"] + team_names,
    #         key="free_kicks_stats_team_name",
    #         label_visibility="visible",
    #     )

    # plot_free_kicks_stats(
    #     players_league_stats, team_name=st.session_state["free_kicks_stats_team_name"]
    # )
    st.write("hello")
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
