from collections import defaultdict
from dataclasses import asdict
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI
from hydra.utils import instantiate
import pandas as pd

from fantasy_helper.db.dao.feature_store.fs_calendar import FSCalendarsDAO
from fantasy_helper.utils.common import load_config
from fantasy_helper.db.utils.create_db import create_db
from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.dao.player import PlayerDAO
from fantasy_helper.db.dao.feature_store.fs_coeffs import FSCoeffsDAO
from fantasy_helper.db.dao.feature_store.fs_lineups import FSLineupsDAO
from fantasy_helper.db.dao.feature_store.fs_players_stats import FSPlayersStatsDAO
from fantasy_helper.db.dao.feature_store.fs_sports_players import FSSportsPlayersDAO

from fantasy_helper.utils.dataclasses import CalendarInfo, MatchInfo, PlayersLeagueStats, SportsPlayerDiff, TeamLineup


cfg = load_config(config_path="../conf", config_name="config")
leagues = {league.ru_name: league.name for league in instantiate(cfg.leagues) if league.is_active}

app = FastAPI()

create_db()
Coeff_dao = CoeffDAO()
Player_dao = PlayerDAO()
FS_Coeff_dao = FSCoeffsDAO()
FS_Lineup_dao = FSLineupsDAO()
FS_Player_dao = FSPlayersStatsDAO()
FS_Sports_Players_dao = FSSportsPlayersDAO()
FS_Calendars_dao = FSCalendarsDAO()


@app.get("/leagues_names/")
async def get_leagues_names() -> Dict[str, str]:
    """
    Get the names of all the leagues.

    Returns:
        A dictionary with league names as keys and league descriptions as values.
    """
    return leagues


@app.get("/players_stats/")
async def get_players_stats(league_name: str) -> Dict:
    """
    Retrieves the statistics of players in a specific league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        Dict: A dictionary containing the players' statistics.
    """
    players_stats = FS_Player_dao.get_players_stats(league_name)
    return players_stats.to_json()


@app.get("/players_stats_teams_names/")
async def get_players_stats_teams_names(league_name: str) -> List[str]:
    """
    Get the names of all teams in the database.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        List[str]: A list of team names in the specified league.
    """
    return FS_Player_dao.get_teams_names(league_name)


@app.get("/players_stats_players_names/")
async def get_players_stats_players_names(league_name: str, team_name: str) -> List[str]:
    """
    Get the names of all players in the database.

    Parameters:
        league_name (str): The name of the league.
        team_name (str): The name of the team.

    Returns:
        List[str]: A list of player names in the specified league and team.
    """
    return FS_Player_dao.get_players_names(league_name, team_name)


@app.get("/coeffs/")
async def get_coeffs(league_name: str, tour: Literal["cur", "next"]) -> List[MatchInfo]:
    """
    Retrieve the coefficients for a given league and tour.

    Parameters:
        league_name (str): The name of the league.
        tour (Literal["cur", "next"]): The tour to retrieve coefficients for.

    Returns:
        List[MatchInfo]: The list of coefficients for the given league and tour.
    """
    return FS_Coeff_dao.get_coeffs(league_name, tour)


@app.get("/tour_number/")
async def get_tour_number(league_name: str) -> Optional[int]:
    """
    Get the tour number for a given league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        int: The tour number for the given league.
    """
    return Coeff_dao.get_tour_number(league_name)


@app.get("/lineups/")
async def get_lineups(league_name: str) -> List[TeamLineup]:
    """
    Retrieves the lineups for a specific league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        List[TeamLineup]: A list of TeamLineup objects representing the lineups for the league.
    """
    return FS_Lineup_dao.get_lineups(league_name)


@app.get("/sports_players/")
async def get_sports_players(league_name: str) -> List[SportsPlayerDiff]:
    return FS_Sports_Players_dao.get_sports_players(league_name)


@app.get("/calendar/")
async def get_calendar(league_name: str) -> List[CalendarInfo]:
    """
    Retrieves the calendars for a specific league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        List[CalendarInfo]: A list of CalendarInfo objects representing the calendars for the league.
    """
    return FS_Calendars_dao.get_calendar(league_name)


@app.get("/players_stats_min_price/")
async def get_players_stats_min_price(league_name: str) -> Optional[float]:
    """
    Get the minimum price for a given league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        int: The minimum price for the given league.
    """
    return FS_Sports_Players_dao.get_min_price(league_name)


@app.get("/players_stats_max_price/")
async def get_players_stats_max_price(league_name: str) -> Optional[float]:
    """
    Get the maximum price for a given league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        int: The maximum price for the given league.
    """
    return FS_Sports_Players_dao.get_max_price(league_name)
