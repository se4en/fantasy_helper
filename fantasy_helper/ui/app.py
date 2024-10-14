from collections import defaultdict
from typing import Dict, List, Literal
import warnings

import requests
import pandas as pd
from pandas.errors import SettingWithCopyWarning
from fantasy_helper.ui.utils.calendar import get_calendar_df, plot_calendar_df
import streamlit as st
import streamlit_authenticator as stauth
from hydra.utils import instantiate

from fantasy_helper.ui.utils.coeffs import get_stat_from_mathes, plot_coeff_df
from fantasy_helper.ui.utils.common import centrize_header
from fantasy_helper.ui.utils.lineups import lineup_to_formation, plot_lineup
from fantasy_helper.ui.utils.players_stats import get_all_stats_columns, get_default_stats_columns, plot_free_kicks_stats, plot_main_players_stats
from fantasy_helper.ui.utils.sports_players import plot_sports_players
from fantasy_helper.utils.common import load_config
from fantasy_helper.utils.dataclasses import CalendarInfo, MatchInfo, PlayersLeagueStats, SportsPlayerDiff, TeamLineup


warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)

api_url = "http://api:8000"
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

authenticator = stauth.Authenticate(
    credentials,
    cookie['name'],
    cookie['key'],
    cookie['expiry_days']
)
try:
    name, authentication_status, username = authenticator.login(location="main")
except KeyError:
    authentication_status = False


@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading coefficients...")
def coeffs_to_df(league_name: str) -> pd.DataFrame:
    """
    Function to convert coefficients to a DataFrame.

    Args:
        league_name (str): The name of the league.

    Returns:
        pd.DataFrame: The DataFrame containing the coefficients information for each team in the league.
    """
    cur_tour_r = requests.get(api_url + f"/coeffs/?league_name={league_name}&tour=cur")
    next_tour_r = requests.get(
        api_url + f"/coeffs/?league_name={league_name}&tour=next"
    )
    cur_tour_number_r = requests.get(
        api_url + f"/tour_number/?league_name={league_name}"
    )

    cur_tour_matches = [MatchInfo(**match) for match in cur_tour_r.json()]
    next_tour_matches = [MatchInfo(**match) for match in next_tour_r.json()]
    cur_tour_number = cur_tour_number_r.json()

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


@st.cache_data(ttl=3600, max_entries=500, show_spinner="Loading players stats...")
def get_players_league_stats(league_name: str) -> PlayersLeagueStats:
    """
    Fetches the players' statistics for a specific league.

    Args:
        league_name (str): The name of the league for which to retrieve the players' statistics.

    Returns:
        PlayersLeagueStats: An instance of the PlayersLeagueStats class containing the fetched statistics.
    """
    r = requests.get(api_url + f"/players_stats/?league_name={league_name}")
    league_stats = PlayersLeagueStats()
    league_stats.from_json(r.json())

    return league_stats


@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading players stats...")
def get_players_stats_teams_names(league_name: str) -> List[str]:
    """
    A function that retrieves the names of teams in a given league.

    Args:
        league_name (str): The name of the league for which team names are to be retrieved.

    Returns:
        List[str]: A list of team names in the specified league.
    """
    r = requests.get(api_url + f"/players_stats_teams_names/?league_name={league_name}")
    return r.json()


@st.cache_data(ttl=600, max_entries=10, show_spinner="Loading lineups...")
def get_lineups(league_name: str) -> List[TeamLineup]:
    """
    Retrieves lineups for a given league.

    Args:
        league_name (str): The name of the league.

    Returns:
        List[TeamLineup]: A list of TeamLineup objects representing the lineups for the league.
    """
    r = requests.get(api_url + f"/lineups/?league_name={league_name}")
    result = [TeamLineup(**lineup) for lineup in r.json()]
    return result


@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading leagues...")
def get_leagues() -> Dict[str, str]:
    """
    A function that retrieves the leagues from the API.

    Args:
        None

    Returns:
        A dictionary containing the names of the leagues and their corresponding IDs.
    """
    r = requests.get(api_url + "/leagues_names/")
    return r.json()


@st.cache_data(ttl=600, max_entries=10, show_spinner="Loading players popularity...")
def get_sports_players(league_name: str) -> List[SportsPlayerDiff]:
    r = requests.get(api_url + f"/sports_players/?league_name={league_name}")
    result = [SportsPlayerDiff(**player) for player in r.json()]
    return result


@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading calendar...")
def calendar_to_df(league_name: str) -> List[CalendarInfo]:
    r = requests.get(api_url + f"/calendar/?league_name={league_name}")
    calendar = [CalendarInfo(**calendar) for calendar in r.json()]
    calendar_df = get_calendar_df(calendar)
    return calendar_df


if authentication_status:
    leagues = get_leagues()
    st.session_state["league"] = list(leagues.values())[0]
    # players stats
    st.session_state["normalize"] = False
    st.session_state["games_count"] = 3
    st.session_state["min_minutes"] = 5

    with st.columns(3)[1]:
        centrize_header("League name")
        st.session_state["league"] = leagues[
            st.selectbox(
                "League name", sorted(leagues.keys()), label_visibility="collapsed"
            )
        ]
    st.write("")

    coeffs_df = coeffs_to_df(st.session_state["league"])
    players_stats = get_players_league_stats(st.session_state["league"])
    players_stats_team_names = get_players_stats_teams_names(st.session_state["league"])
    lineups = get_lineups(st.session_state["league"])
    sports_players = get_sports_players(st.session_state["league"])
    sports_players_team_names = sorted(set([player.team_name for player in sports_players]))
    calendar_df = calendar_to_df(st.session_state["league"])

    left, right = st.columns([4, 2])
    # plot coeffs
    with left:
        centrize_header("Coefficients")
        plot_coeff_df(coeffs_df)

    # plot lineup
    with right:
        centrize_header("Lineups")
        lineups = {lineup.team_name: lineup.lineup for lineup in lineups}
        team_name = st.selectbox(
            "Team", sorted(list(lineups.keys())), label_visibility="visible"
        )
        if team_name is not None:
            formation, positions, names = lineup_to_formation(lineups[team_name])
            if len(positions) == 11 and len(names) == 11:
                fig = plot_lineup(formation, positions, names)
                st.pyplot(fig=fig, clear_figure=None, use_container_width=True)
            else:
                st.write(lineups[team_name])

    # plot calendar
    centrize_header("Calendar")

    columns = st.columns([1, 6])
    with columns[0]:
        st.selectbox(
            "Calendar type",
            options=["points", "goals", "xg"],
            key="calendar_type",
            label_visibility="visible",
        )
    with columns[1]:
        plot_calendar_df(calendar_df, st.session_state["calendar_type"])

    # plot stats
    centrize_header("Players stats")

    columns = st.columns([2, 2, 2, 2])
    with columns[0]:
        st.selectbox(
            "Team name",
            options=["All"] + players_stats_team_names,
            key="player_stats_team_name",
            label_visibility="visible",
        )
    with columns[1]:
        st.session_state["games_count"] = st.number_input(
            "Games count", value=3, min_value=1, max_value=30, step=1
        )
    with columns[2]:
        st.session_state["min_minutes"] = st.number_input(
            "Minimum minutes", value=None, min_value=1, max_value=1000, step=1
        )
    with columns[3]:
        st.write("")
        st.write("")
        st.session_state["normalize"] = st.toggle("Normalize per 90 minutes")

    st.multiselect(
        "Stats columns",
        options=get_all_stats_columns(players_stats),
        default=get_default_stats_columns(players_stats),
        key="stats_columns",
        label_visibility="visible",
    )

    plot_main_players_stats(
        players_stats,
        games_count=st.session_state["games_count"],
        is_abs_stats=not st.session_state["normalize"],
        min_minutes=st.session_state["min_minutes"],
        team_name=st.session_state["player_stats_team_name"],
    )


    columns = st.columns([1, 1])
    with columns[0]:
        # plot free kicks stats
        centrize_header("Free kicks stats")

        subcolumns = st.columns([1, 2, 1])
        with subcolumns[1]:
            st.selectbox(
                "Team name",
                options=["All"] + players_stats_team_names,
                key="free_kicks_stats_team_name",
                label_visibility="visible",
            )

        plot_free_kicks_stats(
            players_stats, team_name=st.session_state["free_kicks_stats_team_name"]
        )

    with columns[1]:
        # plot players popularity
        centrize_header("Players popularity")

        subcolumns = st.columns([1, 2, 1])
        with subcolumns[1]:
            st.selectbox(
                "Team name",
                options=["All"] + sports_players_team_names,
                key="sports_players_team_name",
                label_visibility="visible",
            )

        plot_sports_players(
            sports_players, team_name=st.session_state["sports_players_team_name"]
        )

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
