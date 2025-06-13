from collections import defaultdict
from dataclasses import asdict
import os
import sys
from typing import Dict, List, Literal, Optional
from urllib.parse import urlencode
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from hydra.utils import instantiate
import pandas as pd
from loguru import logger

from fantasy_helper.db.dao.feature_store.fs_calendar import FSCalendarsDAO
from fantasy_helper.utils.common import load_config
from fantasy_helper.db.utils.create_db import create_db
from fantasy_helper.db.dao.coeff import CoeffDAO
from fantasy_helper.db.dao.player import PlayerDAO
from fantasy_helper.db.dao.user import UserDAO
from fantasy_helper.db.dao.feature_store.fs_coeffs import FSCoeffsDAO
from fantasy_helper.db.dao.feature_store.fs_lineups import FSLineupsDAO
from fantasy_helper.db.dao.feature_store.fs_players_stats import FSPlayersStatsDAO
from fantasy_helper.db.dao.feature_store.fs_sports_players import FSSportsPlayersDAO
from fantasy_helper.api.keycloak_client import KeycloakClient
from fantasy_helper.api.auth_dep import get_keycloak_client

from fantasy_helper.utils.dataclasses import CalendarInfo, CalendarTableRow, CoeffTableRow, KeycloakUser, LeagueInfo, MatchInfo, PlayerStatsInfo, PlayersLeagueStats, SportsPlayerDiff, TeamLineup
from fantasy_helper.conf.config import KEYCLOAK_BASE_URL, KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, FRONTEND_URL_HTTPS


cfg = load_config(config_path="../conf", config_name="config")
leagues = {league.ru_name: league.name for league in instantiate(cfg.leagues) if league.is_active}

@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient()
    app.state.keycloak_client = KeycloakClient(http_client)
    yield

    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

# @app.exception_handler(HTTPException)
# async def auth_exception_handler(request: Request, exc: HTTPException):
#     if exc.status_code == 401:
#         return RedirectResponse(
#             f"{settings.auth_url}"
#             f"?client_id={settings.CLIENT_ID}"
#             f"&response_type=code"
#             f"&scope=openid"
#             f"&redirect_uri={settings.redirect_uri}"
#         )
#     raise exc

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dev.fantasy-helper.ru",
        "https://api-dev.fantasy-helper.ru",
        "https://keycloak-dev.fantasy-helper.ru",
    ],
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

create_db()
User_dao = UserDAO()
Coeff_dao = CoeffDAO()
Player_dao = PlayerDAO()
FS_Coeff_dao = FSCoeffsDAO()
FS_Lineup_dao = FSLineupsDAO()
FS_Player_dao = FSPlayersStatsDAO()
FS_Sports_Players_dao = FSSportsPlayersDAO()
FS_Calendars_dao = FSCalendarsDAO()


@app.get("/login/callback/")
async def login_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    keycloak: KeycloakClient = Depends(get_keycloak_client)
) -> JSONResponse:
    if error:
        logger.debug(f"Keycloak error: {error}, description: {error_description}")
        raise HTTPException(status_code=401, detail="Authorization code is required")

    if not code:
        logger.debug(f"Authorization code is required")
        raise HTTPException(status_code=401, detail="Authorization code is required")

    try:
        # Получение токенов от Keycloak
        token_data = await keycloak.get_tokens(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        id_token = token_data.get("id_token")

        if not access_token:
            logger.error(f"Токен доступа не найден")
            raise HTTPException(status_code=401, detail="Токен доступа не найден")
        if not refresh_token:
            logger.error(f"Refresh token не найден")
            raise HTTPException(status_code=401, detail="Refresh token не найден")
        if not id_token:
            logger.error(f"ID token не найден")
            raise HTTPException(status_code=401, detail="ID token не найден")

        # Получение информации о пользователе
        user_info = await keycloak.get_user_info(access_token)
        user_id = user_info.get("sub")
        if not user_id:
            logger.error(f"ID пользователя не найден")
            raise HTTPException(status_code=401, detail="ID пользователя не найден")

        # Проверка существования пользователя, создание нового при необходимости
        user = User_dao.get_user_by_id(user_id)
        logger.info(f"user get_user_by_id: {user}")
        if not user and isinstance(user_info, dict):
            user_info["id"] = user_info.pop("sub")
            user = KeycloakUser(
                id=user_info["id"],
                email=user_info["email"],
                email_verified=user_info["email_verified"],
                name=user_info["name"],
                preferred_username=user_info["preferred_username"],
                given_name=user_info["given_name"],
                family_name=user_info["family_name"],
            )
            User_dao.add_user(user)

        response = JSONResponse(content={"message": "Login successful"}) 
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=token_data.get("refresh_expires_in", 2592000),
        )
        response.set_cookie(
            key="id_token",
            value=id_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=token_data.get("expires_in", 3600),
        )
        logger.debug(f"User {user_id} logged in successfully")
        return response

    except Exception as e:
        exc_type, exc_value, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Ошибка обработки callback'а логина: {exc_type}, {fname}, {exc_tb.tb_lineno}")
        raise HTTPException(status_code=401, detail="Ошибка авторизации")


@app.get("/logout")
async def logout(request: Request):
    id_token = request.cookies.get("id_token")
    params = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "post_logout_redirect_uri": KEYCLOAK_BASE_URL,
    }
    if id_token:
        params["id_token_hint"] = id_token

    keycloak_logout_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
    full_logout_url = f"{keycloak_logout_url}?{urlencode(params)}"
    response = RedirectResponse(url=full_logout_url)
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    response.delete_cookie(
        key="id_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )
    return response


@app.get("/leagues_info/")
async def get_leagues_info() -> List[LeagueInfo]:
    """
    Get the names of all the leagues.

    Returns:
        A dictionary with league names as keys and league descriptions as values.
    """
    result = []
    for league_config in cfg.leagues:
        result.append(instantiate(league_config))
    return result


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


@app.get("/players_stats_info/")
async def get_players_stats_info(league_name: str) -> List[PlayerStatsInfo]:
    players_stats_info = FS_Player_dao.get_players_stats_info(league_name)
    return players_stats_info


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
async def get_coeffs(league_name: str) -> List[CoeffTableRow]:
    return FS_Coeff_dao.get_coeffs(league_name)


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
async def get_calendar(league_name: str) -> List[CalendarTableRow]:
    return FS_Calendars_dao.get_calendar(league_name)


@app.get("/players_stats_prices/")
async def get_players_stats_prices(league_name: str) -> List[float]:
    """
    Get the maximum price for a given league.

    Parameters:
        league_name (str): The name of the league.

    Returns:
        int: The maximum price for the given league.
    """
    return FS_Sports_Players_dao.get_players_prices(league_name)
