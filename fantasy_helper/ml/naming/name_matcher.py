from typing import Any, Dict, List, Optional, Tuple
import os.path as path
import json
from datetime import datetime

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_
from openai import OpenAI
import httpx
from loguru import logger

from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.actual_player import ActualPlayer
from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.database import Session
from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD, OPENROUTER_API_KEY
from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerName, TeamName


class NameMatcher:
    def __init__(self, openai_model: str = "deepseek/deepseek-chat-v3-0324:free"):
        proxy_url = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
        self._openai_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
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
            db_session.query(ActualPlayer.team_name).filter(
                ActualPlayer.league_name == league_name
            )
            .distinct()
            .order_by(ActualPlayer.team_name)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]

    def get_fbref_players_names(self, league_name: str, team_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(ActualPlayer.name).filter(and_(
                ActualPlayer.league_name == league_name,
                ActualPlayer.team_name == team_name
            ))
            .distinct()
            .order_by(ActualPlayer.name)
        )
        players_names = query.all()

        db_session.close()

        return [elem[0] for elem in players_names]

    def get_xbet_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Coeff.home_team).filter(and_(
                Coeff.league_name == league_name,
                Coeff.timestamp <= datetime(2025, 4, 15)
            ))
            .distinct()
            .order_by(Coeff.home_team)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]
    
    def get_betcity_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        home_query = (
            db_session.query(Coeff.home_team).filter(and_(
                Coeff.league_name == league_name,
                Coeff.timestamp > datetime(2025, 4, 15)
            ))
            .distinct()
            .order_by(Coeff.home_team)
        )
        home_team_names = home_query.all()

        away_query = (
            db_session.query(Coeff.away_team).filter(and_(
                Coeff.league_name == league_name,
                Coeff.timestamp > datetime(2025, 4, 15)
            ))
            .distinct()
            .order_by(Coeff.away_team)
        )
        away_team_names = away_query.all()

        db_session.close()

        all_team_names = [elem[0] for elem in home_team_names] + [elem[0] for elem in away_team_names]
        return sorted(set(all_team_names))

    def _get_match_teams_names(self, teams_names_1: List[str], teams_names_2: List[str]) -> Dict[str, str]:
        if len(teams_names_1) == 0 or len(teams_names_2) == 0:
            return {}

        try:
            user_message = {"role": "user", "content": f"list 1: {teams_names_1}, list 2: {teams_names_2}"}
            completion = self._openai_client.chat.completions.create(
                model=self._openai_model,
                messages=self._teams_names_prompt + [user_message],
                response_format={"type": "json_object"},
            )

            if completion.choices is None:
                logger.warning(f"Failed to match teams names for {teams_names_1[0]}... {teams_names_2[0]}...")
                return {}

            result = json.loads(completion.choices[0].message.content)
            logger.info(f"Successfully matched {len(result)} teams names for {teams_names_1[0]}... {teams_names_2[0]}...")
            return result
        except self._openai_client.APIConnectionError as e:
            logger.warning(f"API connection error when matching teams names: {e}")
            return {}
        except self._openai_client.APITimeoutError as e:
            logger.warning(f"API timeout error when matching teams names: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse response for {teams_names_1[0]}... {teams_names_2[0]}...")
            return {}

    def match_teams_names(self, teams_names_1: List[str], teams_names_2: List[str]) -> Dict[str, str]:
        result = self._get_match_teams_names(teams_names_1, teams_names_2)
        teams_names_1_add = list(filter(lambda x: x not in result.keys(), teams_names_1))
        teams_names_2_add = list(filter(lambda x: x not in result.values(), teams_names_2))
        result.update(self._get_match_teams_names(teams_names_1_add, teams_names_2_add))
        return result

    def _get_match_players_names(self, players_names_1: List[str], players_names_2: List[str]) -> Dict[str, str]:
        if len(players_names_1) == 0 or len(players_names_2) == 0:
            return {}

        try:
            user_message = {"role": "user", "content": f"list 1: {players_names_1}, list 2: {players_names_2}"}
            completion = self._openai_client.chat.completions.create(
                model=self._openai_model,
                messages=self._players_names_prompt + [user_message],
                response_format={"type": "json_object"},
            )

            if completion.choices is None:
                logger.warning(f"Failed to match players names for {players_names_1[0]}... {players_names_2[0]}...")
                return {}

            result = json.loads(completion.choices[0].message.content)
            logger.info(f"Successfully matched {len(result)} players names for {players_names_1[0]}... {players_names_2[0]}...")
            return result
        except self._openai_client.APIConnectionError as e:
            logger.warning(f"API connection error when matching players names: {e}")
            return {}
        except self._openai_client.APITimeoutError as e:
            logger.warning(f"API timeout error when matching players names: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse response for {players_names_1[0]}... {players_names_2[0]}...")
            return {}

    def match_players_names(self, players_names_1: List[str], players_names_2: List[str]) -> Dict[str, str]:
        result = self._get_match_players_names(players_names_1, players_names_2)
        players_names_1_add = list(filter(lambda x: x not in result.keys(), players_names_1))
        players_names_2_add = list(filter(lambda x: x not in result.values(), players_names_2))
        result.update(self._get_match_players_names(players_names_1_add, players_names_2_add))
        return result
    
    def _compute_free_and_delete_elements(
            self, cur_names: List[str], cur_name_2_elem: Dict[str, Any]
        ) -> Tuple[List[str], List[Any]]:
        free_names, elems_to_delete = [], []

        for cur_name in cur_names:
            if cur_name in cur_name_2_elem:
                del cur_name_2_elem[cur_name]
            else:
                free_names.append(cur_name)
        for name, elem in cur_name_2_elem.items():
            elems_to_delete.append(elem)
        
        return free_names, elems_to_delete

    def match_teams(self, league_name: str, teams_names: List[TeamName]) -> Tuple[List[TeamName], List[TeamName]]:
        cur_sports_teams_names = self.get_sports_teams_names(league_name)
        cur_fbref_teams_names = self.get_fbref_teams_names(league_name)
        cur_xbet_teams_names = self.get_xbet_teams_names(league_name)
        cur_betcity_teams_names = self.get_betcity_teams_names(league_name)
        logger.info(f"Cur teams names for {league_name}: sports({len(cur_sports_teams_names)}), fbref({len(cur_fbref_teams_names)}), xbet({len(cur_xbet_teams_names)}), betcity({len(cur_betcity_teams_names)})")

        free_sports_teams_names, free_fbref_teams_names, free_xbet_teams_names, free_betcity_teams_names = [], [], [], []
        teams_to_add, teams_to_delete = [], []

        cur_sports_name_2_team = {
            team_name.sports_name: team_name 
            for team_name in teams_names if team_name.sports_name
        }
        cur_fbref_name_2_team = {
            team_name.fbref_name: team_name 
            for team_name in teams_names if team_name.fbref_name
        }
        cur_xbet_name_2_team = {
            team_name.xbet_name: team_name 
            for team_name in teams_names if team_name.xbet_name
        }
        cur_betcity_name_2_team = {
            team_name.betcity_name: team_name 
            for team_name in teams_names if team_name.betcity_name
        }

        free_sports_teams_names, sports_teams_to_delete = self._compute_free_and_delete_elements(
            cur_sports_teams_names, cur_sports_name_2_team
        )
        free_fbref_teams_names, fbref_teams_to_delete = self._compute_free_and_delete_elements(
            cur_fbref_teams_names, cur_fbref_name_2_team
        )
        free_xbet_teams_names, xbet_teams_to_delete = self._compute_free_and_delete_elements(
            cur_xbet_teams_names, cur_xbet_name_2_team
        )
        free_betcity_teams_names, betcity_teams_to_delete = self._compute_free_and_delete_elements(
            cur_betcity_teams_names, cur_betcity_name_2_team
        )

        # remove dublicated teams
        if sports_teams_to_delete or fbref_teams_to_delete or xbet_teams_to_delete or betcity_teams_to_delete:
            teams_to_delete = list(dict.fromkeys(
                sports_teams_to_delete + fbref_teams_to_delete + xbet_teams_to_delete + betcity_teams_to_delete
            ))

        # compute new teams names
        if free_sports_teams_names or free_fbref_teams_names or free_xbet_teams_names or free_betcity_teams_names:
            sports_2_fbref_teams = self.match_teams_names(free_sports_teams_names, free_fbref_teams_names)
            sports_2_xbet_teams = self.match_teams_names(free_sports_teams_names, free_xbet_teams_names)
            sports_2_betcity_teams = self.match_teams_names(free_sports_teams_names, free_betcity_teams_names)

            if len(sports_2_betcity_teams) > len(sports_2_fbref_teams):
                for k, v in sports_2_betcity_teams.items():
                    teams_to_add.append(TeamName(
                        league_name=league_name,
                        sports_name=k,
                        fbref_name=sports_2_fbref_teams.get(k),
                        xbet_name=sports_2_xbet_teams.get(k),
                        betcity_name=v
                    ))
            elif len(sports_2_fbref_teams) > len(sports_2_xbet_teams):
                for k, v in sports_2_fbref_teams.items():
                    teams_to_add.append(TeamName(
                        league_name=league_name,
                        sports_name=k,
                        fbref_name=v,
                        xbet_name=sports_2_xbet_teams.get(k),
                        betcity_name=sports_2_betcity_teams.get(k)
                    ))
            else:
                for k, v in sports_2_xbet_teams.items():
                    teams_to_add.append(TeamName(
                        league_name=league_name,
                        sports_name=k,
                        fbref_name=sports_2_fbref_teams.get(k),
                        xbet_name=v,
                        betcity_name=sports_2_betcity_teams.get(k)
                    ))

        return teams_to_add, teams_to_delete

    def match_players(
            self, league_name: str, team_name: TeamName, players_names: List[PlayerName]
        ) -> Tuple[List[PlayerName], List[PlayerName]]:
        cur_sports_players_names = self.get_sports_players_names(league_name, team_name.sports_name)
        cur_fbref_players_names = self.get_fbref_players_names(league_name, team_name.fbref_name)
        logger.info(f"Cur players names for {team_name.name} in {league_name}: sports({len(cur_sports_players_names)}), fbref({len(cur_fbref_players_names)})")

        free_sports_players_names, free_fbref_players_names = [], []
        players_to_add, players_to_delete = [], []

        cur_sports_name_2_player = {player_name.sports_name: player_name for player_name in players_names}
        cur_fbref_name_2_player = {player_name.fbref_name: player_name for player_name in players_names}

        free_sports_players_names, sports_players_to_delete = self._compute_free_and_delete_elements(
            cur_sports_players_names, cur_sports_name_2_player
        )
        free_fbref_players_names, fbref_players_to_delete = self._compute_free_and_delete_elements(
            cur_fbref_players_names, cur_fbref_name_2_player
        )

        # remove dublicated players
        if sports_players_to_delete or fbref_players_to_delete:
            players_to_delete = list(dict.fromkeys(
                sports_players_to_delete + fbref_players_to_delete
            ))

        # compute new players names
        if free_sports_players_names or free_fbref_players_names:
            sports_2_fbref_players = self.match_players_names(free_sports_players_names, free_fbref_players_names)

            for k, v in sports_2_fbref_players.items():
                players_to_add.append(PlayerName(
                    league_name=league_name,
                    team_name=team_name.name,
                    sports_name=k, 
                    fbref_name=v,
                ))

        return players_to_add, players_to_delete
