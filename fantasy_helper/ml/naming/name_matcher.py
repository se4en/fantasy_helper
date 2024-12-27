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
from fantasy_helper.db.database import Session
from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD, OPENAI_API_KEY
from fantasy_helper.utils.dataclasses import PlayerName, TeamName


class NameMatcher:
    def __init__(self, openai_model: str = "gpt-4o-mini-2024-07-18"):
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

    def _get_match_teams_names(self, teams_names_1: List[str], teams_names_2: List[str]) -> Dict[str, str]:
        user_message = {"role": "user", "content": f"list 1: {teams_names_1}, list 2: {teams_names_2}"}
        completion = self._openai_client.chat.completions.create(
            model=self._openai_model,
            messages=self._teams_names_prompt + [user_message],
        )
        try:
            return json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError as e:
            return {}

    def match_teams_names(self, teams_names_1: List[str], teams_names_2: List[str]) -> Dict[str, str]:
        result = self._get_match_teams_names(teams_names_1, teams_names_2)
        teams_names_1_add = list(filter(lambda x: x not in result.keys(), teams_names_1))
        teams_names_2_add = list(filter(lambda x: x not in result.values(), teams_names_2))
        result.update(self._get_match_teams_names(teams_names_1_add, teams_names_2_add))
        return result

    def _get_match_players_names(self, players_names_1: List[str], players_names_2: List[str]) -> Dict[str, str]:
        user_message = {"role": "user", "content": f"list 1: {players_names_1}, list 2: {players_names_2}"}
        completion = self._openai_client.chat.completions.create(
            model=self._openai_model,
            messages=self._players_names_prompt + [user_message],
        )
        try:
            return json.loads(completion.choices[0].message.content)
        except json.JSONDecodeError as e:
            return {}

    def match_players_names(self, players_names_1: List[str], players_names_2: List[str]) -> Dict[str, str]:
        result = self._get_match_players_names(players_names_1, players_names_2)
        players_names_1_add = list(filter(lambda x: x not in result.keys(), players_names_1))
        players_names_2_add = list(filter(lambda x: x not in result.values(), players_names_2))
        result.update(self._get_match_players_names(players_names_1_add, players_names_2_add))
        return result

    def match_teams(self, league_name: str) -> List[TeamName]:
        sports_teams_names = self.get_sports_teams_names(league_name)
        fbref_teams_names = self.get_fbref_teams_names(league_name)
        xbet_teams_names = self.get_xbet_teams_names(league_name)

        sports_2_fbref_teams = self.match_teams_names(sports_teams_names, fbref_teams_names)
        sports_2_xbet_teams = self.match_teams_names(sports_teams_names, xbet_teams_names)

        result = []
        for k, v in sports_2_fbref_teams.items():
            result.append(TeamName(
                league_name=league_name,
                sports_name=k,
                fbref_name=v,
                xbet_name=sports_2_xbet_teams.get(k)
            ))

        return result

    def match_players(self, league_name: str, team_name: TeamName) -> List[PlayerName]:
        sports_players_names = self.get_sports_players_names(league_name, team_name.sports_name)
        fbref_players_names = self.get_fbref_players_names(league_name, team_name.fbref_name)

        sports_2_fbref_players = self.match_players_names(sports_players_names, fbref_players_names)

        result = []
        for k, v in sports_2_fbref_players.items():
            result.append(PlayerName(
                league_name=league_name,
                team_name=team_name.name,
                sports_name=k, 
                fbref_name=v,
            ))

        return result
