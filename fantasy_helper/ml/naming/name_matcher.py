from typing import Dict, List, Optional
import os.path as path
import json

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_
from openai import OpenAI
import httpx

from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.player import Player
from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.db.database import Session
from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD, OPENAI_API_KEY
from fantasy_helper.utils.dataclasses import LeagueInfo


class NameMatcher:
    def __init__(self, openai_model: str = "gpt-4o-2024-11-20"):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
        self._openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            http_client=httpx.Client(proxy=proxy_url)
        )
        self._openai_model = openai_model

        self._teams_names_prompt = json.load(
            open(path.join(path.dirname(__file__), "prompts/teams_names.json"), "r")
        )
        self._players_names_prompt = json.load(
            open(path.join(path.dirname(__file__), "prompts/players_names.json"), "r")
        )

    def get_sports_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(SportsPlayer.team_name).filter(
                SportsPlayer.league_name == league_name
            )
            .distinct()
            .order_by(SportsPlayer.team_name)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]

    def get_sports_players_names(self, league_name: str, team_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(SportsPlayer.name).filter(and_(
                SportsPlayer.league_name == league_name,
                SportsPlayer.team_name == team_name
            ))
            .distinct()
            .order_by(SportsPlayer.name)
        )
        players_names = query.all()

        db_session.close()

        return [elem[0] for elem in players_names]

    def get_fbref_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Player.team_name).filter(
                Player.league_name == league_name
            )
            .distinct()
            .order_by(Player.team_name)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]

    def get_fbref_players_names(self, league_name: str, team_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Player.name).filter(and_(
                Player.league_name == league_name,
                Player.team_name == team_name
            ))
            .distinct()
            .order_by(Player.name)
        )
        players_names = query.all()

        db_session.close()

        return [elem[0] for elem in players_names]

    def get_xbet_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Coeff.home_team).filter(
                Coeff.league_name == league_name
            )
            .distinct()
            .order_by(Coeff.home_team)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]

    def match_teams_names(self, teams_names_1: List[str], teams_names_2: List[str]) -> Dict[str, str]:
        user_message = {"role": "user", "content": f"list 1: {teams_names_1}, list 2: {teams_names_2}"}
        completion = self._openai_client.chat.completions.create(
            model=self._openai_model,
            messages=self._teams_names_prompt + [user_message],
        )
        return completion.choices[0].message.content

    def match_players_names(self, players_names_1: List[str], players_names_2: List[str]) -> Dict[str, str]:
        user_message = {"role": "user", "content": f"list 1: {players_names_1}, list 2: {players_names_2}"}
        completion = self._openai_client.chat.completions.create(
            model=self._openai_model,
            messages=self._players_names_prompt + [user_message],
        )
        return completion.choices[0].message.content

    def get_leagues_names(self) -> List[str]:
        return [league.name for league in self._leagues]


if __name__ == "__main__":
    matcher = NameMatcher()
    
    # sports_names = matcher.get_sports_teams_names("Russia")
    # fbref_names = matcher.get_fbref_teams_names("Russia")
    # xbet_names = matcher.get_xbet_teams_names("Russia")

    team_1 = matcher.get_sports_players_names("England", "Астон Вилла")
    team_2 = matcher.get_fbref_players_names("England", "Aston Villa")

    result = matcher.match_players_names(team_1, team_2)

    print("list 1", team_1)
    print("")
    print("list 2", team_2)
    print("")
    print("result", result)
