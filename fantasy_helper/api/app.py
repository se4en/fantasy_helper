from collections import defaultdict
from dataclasses import asdict
from typing import Dict, List, Literal

from fastapi import FastAPI
from hydra.utils import instantiate
import pandas as pd

from fantasy_helper.api.utils import get_stat_from_mathes
from fantasy_helper.utils.common import load_config
from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.dao.lineup import LineupDAO
from fantasy_helper.db.dao.player import PlayerDAO
from fantasy_helper.utils.dataclasses import MatchInfo, PlayersLeagueStats, TeamLineup


cfg = load_config(config_path="../conf", config_name="config")
leagues = {league.ru_name: league.name for league in instantiate(cfg.leagues)}

app = FastAPI()

Coeff_dao = CoeffDAO()
Lineup_dao = LineupDAO()
Player_dao = PlayerDAO()


@app.get("/leagues_names")
async def get_leagues_names() -> Dict[str, str]:
    return leagues


@app.get("/players_stats")
async def get_players_stats(league_name: str) -> dict:
    players_stats = Player_dao.get_players_stats(league_name)
    return players_stats.to_json()


@app.get("/coeffs")
async def get_coeffs(league_name: str, tour: Literal["cur", "next"]) -> List[MatchInfo]:
    return Coeff_dao.get_coeffs(league_name, tour)


@app.get("/tour_number")
async def get_coeffs(league_name: str) -> int:
    return Coeff_dao.get_tour_number(league_name)


@app.get("/players_teams_names")
async def get_players_teams_names(league_name: str) -> List[str]:
    return Player_dao.get_teams_names(league_name)


@app.get("/lineups")
async def get_lineups(league_name: str) -> List[TeamLineup]:
    return Lineup_dao.get_lineups(league_name)
