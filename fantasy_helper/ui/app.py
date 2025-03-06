from collections import defaultdict
from typing import Dict, List, Literal, Optional
import warnings

import requests
import pandas as pd
from pandas.errors import SettingWithCopyWarning
from fantasy_helper.ui.utils.calendar import get_calendar_df, plot_calendar_df
import streamlit as st
import streamlit_authenticator as stauth
from hydra.utils import instantiate

from fantasy_helper.ui.utils.coeffs import get_coeffs_info_from_mathes, get_unique_teams, plot_coeff_df
from fantasy_helper.ui.utils.common import centrize_header, centrize_text
from fantasy_helper.ui.utils.lineups import lineup_to_formation, plot_lineup
from fantasy_helper.ui.utils.players_stats import get_available_stats_columns, get_default_stats_columns, get_player_stats, plot_free_kicks_stats, plot_main_players_stats, plot_players_stats_diff, prepare_players_stats_df
from fantasy_helper.ui.utils.sports_players import get_available_positions, plot_sports_players
from fantasy_helper.utils.common import load_config
from fantasy_helper.utils.dataclasses import CalendarInfo, MatchInfo, PlayerStatsInfo, PlayersLeagueStats, SportsPlayerDiff, TeamLineup


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
    matches_r = requests.get(api_url + f"/coeffs/?league_name={league_name}")
    matches = [MatchInfo(**match) for match in matches_r.json()]
    unique_teams = get_unique_teams(matches)
    coeffs_info = get_coeffs_info_from_mathes(matches, unique_teams)

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
def get_players_stats_info(league_name: str) -> List[PlayerStatsInfo]:
    r = requests.get(api_url + f"/players_stats_info/?league_name={league_name}")
    players_stats = [PlayerStatsInfo(**player_stats) for player_stats in r.json()]
    return players_stats


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


@st.cache_data(ttl=3600, max_entries=10, show_spinner="Loading players stats...")
def get_players_stats_players_names(league_name: str, team_name: str) -> List[str]:
    """
    A function that retrieves the names of players in a given league and team.

    Args:
        league_name (str): The name of the league for which player names are to be retrieved.
        team_name (str): The name of the team for which player names are to be retrieved.

    Returns:
        List[str]: A list of player names in the specified league and team.
    """
    r = requests.get(api_url + f"/players_stats_players_names/?league_name={league_name}&team_name={team_name}")
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


@st.cache_data(ttl=36000, max_entries=10, show_spinner="Loading players prices...")
def get_players_stats_prices(league_name: str) -> List[float]:
    r = requests.get(api_url + f"/players_stats_prices/?league_name={league_name}")
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
    st.session_state["normalize_minutes"] = False
    st.session_state["normalize_matches"] = False
    st.session_state["games_count"] = 3
    st.session_state["min_minutes"] = 5

    with st.columns(3)[1]:
        centrize_header("Чемпионат")
        st.session_state["league"] = leagues[
            st.selectbox(
                "League name", sorted(leagues.keys()), label_visibility="collapsed"
            )
        ]
    st.write("")

    coeffs_df = coeffs_to_df(st.session_state["league"])
    players_stats = get_players_league_stats(st.session_state["league"])
    players_stats_info = get_players_stats_info(st.session_state["league"])
    players_stats_team_names = get_players_stats_teams_names(st.session_state["league"])
    players_stats_positions = get_available_positions()
    players_stats_prices = get_players_stats_prices(st.session_state["league"])
    lineups = get_lineups(st.session_state["league"])
    sports_players = get_sports_players(st.session_state["league"])
    sports_players_team_names = sorted(set([player.team_name for player in sports_players]))
    calendar_df = calendar_to_df(st.session_state["league"])

    left, right = st.columns([4, 2])
    # plot coeffs
    with left:
        centrize_header("Котировки")
        plot_coeff_df(coeffs_df)

    # plot lineup
    with right:
        centrize_header("Составы")
        lineups = {lineup.team_name: lineup.lineup for lineup in lineups}
        team_name = st.selectbox(
            "Команда", sorted(list(lineups.keys())), label_visibility="visible"
        )
        if team_name is not None:
            formation, positions, names = lineup_to_formation(lineups[team_name])
            if len(positions) == 11 and len(names) == 11:
                fig = plot_lineup(formation, positions, names)
                st.pyplot(fig=fig, clear_figure=None, use_container_width=True)
            else:
                st.write(lineups[team_name])

    # plot calendar
    centrize_header("Календарь")

    columns = st.columns([1, 6])
    with columns[0]:
        st.selectbox(
            "Тип календаря",
            options=["points", "goals", "xg"],
            key="calendar_type",
            label_visibility="visible",
        )
    with columns[1]:
        plot_calendar_df(calendar_df, st.session_state["calendar_type"])

    # plot stats
    centrize_header("Статистика игроков")

    columns = st.columns([2, 1, 1, 1, 2, 2, 2, 2])
    with columns[0]:
        st.selectbox(
            "Команда",
            options=["All"] + players_stats_team_names,
            key="player_stats_team_name",
            label_visibility="visible"
        )
    with columns[1]:
        st.selectbox(
            "Позиция",
            options=["All"] + players_stats_positions,
            key="player_stats_position",
            label_visibility="visible"
        )
    with columns[2]:
        st.selectbox(
            "Мин цена",
            options=players_stats_prices,
            key="player_min_price",
            label_visibility="visible",
            index=0
        )
    with columns[3]:
        st.selectbox(
            "Макс цена",
            options=players_stats_prices,
            key="player_max_price",
            label_visibility="visible",
            index=len(players_stats_prices) - 1
        )
    with columns[4]:
        st.session_state["games_count"] = st.number_input(
            "Последние матчи", value=3, min_value=1, max_value=30, step=1
        )
    with columns[5]:
        st.session_state["min_minutes"] = st.number_input(
            "Минимум минут", value=None, min_value=1, max_value=1000, step=1
        )
    with columns[6]:
        st.write("")
        st.write("")
        st.session_state["normalize_minutes"] = st.toggle("Нормировать на 90 мин")
    with columns[7]:
        st.write("")
        st.write("")
        st.session_state["normalize_matches"] = st.toggle("Нормировать на матчи")

    players_stats_df = prepare_players_stats_df(
        players_stats_info,
        games_count=st.session_state["games_count"],
        normalize_minutes=st.session_state["normalize_minutes"],
        normalize_matches=st.session_state["normalize_matches"],
        min_minutes=st.session_state["min_minutes"]
    )

    available_stats_columns = get_available_stats_columns(players_stats_df)
    default_stats_columns = get_default_stats_columns(players_stats_df)
    st.multiselect(
        "Выбранные опции",
        options=available_stats_columns,
        default=default_stats_columns,
        key="player_stats_column_names",
        label_visibility="visible",
    )

    plot_main_players_stats(
        players_stats_df,
        st.session_state["player_stats_column_names"],
        st.session_state["player_stats_team_name"],
        st.session_state["player_stats_position"],
        st.session_state["player_min_price"],
        st.session_state["player_max_price"]
    )

    # player comparison
    columns = st.columns([4, 4, 1, 4, 4])
    with columns[0]:
        st.selectbox(
            "Команда",
            options=["All"] + players_stats_team_names,
            key="player_stats_team_name_left",
            label_visibility="visible",
        )
    with columns[1]:
        players_stats_players_names_left = get_players_stats_players_names(
            st.session_state["league"],
            st.session_state["player_stats_team_name_left"]
        )
        st.selectbox(
            "Имя",
            options=["All"] + players_stats_players_names_left,
            key="player_stats_player_name_left",
            label_visibility="visible",
        )
    with columns[2]:
        st.write("")
        centrize_text("vs")
    with columns[3]:
        st.selectbox(
            "Команда",
            options=["All"] + players_stats_team_names,
            key="player_stats_team_name_right",
            label_visibility="visible",
        )
    with columns[4]:
        players_stats_players_names_right = get_players_stats_players_names(
            st.session_state["league"],
            st.session_state["player_stats_team_name_right"]
        )
        st.selectbox(
            "Имя",
            options=["All"] + players_stats_players_names_right,
            key="player_stats_player_name_right",
            label_visibility="visible",
        )
    
    left_player = get_player_stats(
        players_stats_df,
        team_name=st.session_state["player_stats_team_name_left"],
        name=st.session_state["player_stats_player_name_left"]
    )
    right_player = get_player_stats(
        players_stats_df,
        team_name=st.session_state["player_stats_team_name_right"],
        name=st.session_state["player_stats_player_name_right"]
    )
    plot_players_stats_diff(
        left_player, 
        right_player,
        st.session_state["player_stats_column_names"]
    )

    columns = st.columns([1, 1])
    # plot free kicks stats
    with columns[0]:
        centrize_header("Исполнители стандартов")

        subcolumns = st.columns([1, 2, 1])
        with subcolumns[1]:
            st.selectbox(
                "Команда",
                options=["All"] + players_stats_team_names,
                key="free_kicks_stats_team_name",
                label_visibility="visible",
            )

        plot_free_kicks_stats(
            players_stats, team_name=st.session_state["free_kicks_stats_team_name"]
        )
    # plot players popularity
    with columns[1]:
        centrize_header("Популярность игроков")

        subcolumns = st.columns([1, 2, 1])
        with subcolumns[1]:
            st.selectbox(
                "Команда",
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
