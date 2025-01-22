from copy import deepcopy
from dataclasses import asdict
from typing import List
from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession
import pandas as pd

from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerName, SportsPlayerDiff, TeamName, PlayersLeagueStats
from fantasy_helper.db.database import Session
from fantasy_helper.db.models.ml.player_name import PlayerName as DBPlayerName
from fantasy_helper.db.models.ml.team_name import TeamName as DBTeamName
from fantasy_helper.ml.naming.name_matcher import NameMatcher


utc = timezone.utc


class NamingDAO:
    def __init__(self, logger = None):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._name_matcher = NameMatcher()

    def update_league_naming(self, league_name: str) -> None:
        teams_names = self._get_teams_names(league_name)

        # update teams names
        teams_names_to_add, teams_names_to_delete = self._name_matcher.match_teams(
            league_name=league_name, 
            teams_names=teams_names
        )
        self._delete_teams_names(teams_names_to_delete)
        self._add_teams_names(teams_names_to_add)

        # update players names
        new_teams_names = self._get_teams_names(league_name)
        for team_name in new_teams_names:
            players_names = self._get_players_names(league_name, team_name.name)
            players_names_to_add, players_names_to_delete = self._name_matcher.match_players(
                league_name=league_name, 
                team_name=team_name,
                players_names=players_names
            )
            self._delete_players_names(players_names_to_delete)
            self._add_players_names(players_names_to_add)

    def _get_teams_names(self, league_name: str) -> List[TeamName]:
        db_session: SQLSession = Session()

        teams_names = (
            db_session.query(DBTeamName)
            .filter(DBTeamName.league_name == league_name)
            .all()
        )

        result = [
            TeamName(
                league_name=team.league_name,
                sports_name=team.sports_name,
                fbref_name=team.fbref_name,
                xbet_name=team.xbet_name,
                name=team.name
            ) 
            for team in teams_names
        ]

        db_session.commit()
        db_session.close()

        return result

    def _add_teams_names(self, teams_names: List[TeamName]) -> None:
        db_session: SQLSession = Session()

        for team_name in teams_names:
            db_session.add(DBTeamName(
                timestamp=datetime.now().replace(tzinfo=utc), 
                **asdict(team_name)
            ))

        db_session.commit()
        db_session.close()

    def _delete_teams_names(self, teams_names: List[TeamName]) -> None:
        db_session: SQLSession = Session()

        for team_name in teams_names:
            db_session.query(DBTeamName).filter(and_(
                DBTeamName.league_name == team_name.league_name,
                DBTeamName.name == team_name.name,
                DBTeamName.sports_name == team_name.sports_name,
                DBTeamName.fbref_name == team_name.fbref_name,
                DBTeamName.xbet_name == team_name.xbet_name
            )).delete()

        db_session.commit()
        db_session.close()

    def _get_players_names(self, league_name: str, team_name: str) -> List[PlayerName]:
        db_session: SQLSession = Session()

        players_names = (
            db_session.query(DBPlayerName)
            .filter(and_(
                DBPlayerName.league_name == league_name, 
                DBPlayerName.team_name == team_name
            ))
            .all()
        )

        result = [
            PlayerName(
                league_name=player.league_name,
                team_name=player.team_name,
                sports_name=player.sports_name,
                fbref_name=player.fbref_name,
                name=player.name
            ) 
            for player in players_names
        ]

        db_session.commit()
        db_session.close()

        return result
    
    def _add_players_names(self, players_names: List[PlayerName]) -> None:
        db_session: SQLSession = Session()

        for player_name in players_names:
            db_session.add(DBPlayerName(
                timestamp=datetime.now().replace(tzinfo=utc), 
                **asdict(player_name)
            ))

        db_session.commit()
        db_session.close()

    def _delete_players_names(self, players_names: List[PlayerName]) -> None:
        db_session: SQLSession = Session()

        for player_name in players_names:
            db_session.query(DBPlayerName).filter(and_(
                DBPlayerName.league_name == player_name.league_name,
                DBPlayerName.name == player_name.name,
                DBPlayerName.team_name == player_name.team_name,
                DBPlayerName.sports_name == player_name.sports_name,
                DBPlayerName.fbref_name == player_name.fbref_name
            )).delete()

        db_session.commit()
        db_session.close()

    def update_naming_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_league_naming(league.name)

    def get_teams(self, league_name: str) -> List[TeamName]:
        db_session: SQLSession = Session()

        teams = (
            db_session.query(DBTeamName)
            .filter(DBTeamName.league_name == league_name)
            .all()
        )

        result = [
            TeamName(
                league_name=team.league_name,
                sports_name=team.sports_name,
                fbref_name=team.fbref_name,
                xbet_name=team.xbet_name,
                name=team.name
            ) 
            for team in teams
        ]

        db_session.commit()
        db_session.close()
    
        return result

    def get_players(self, league_name: str) -> List[PlayerName]:
        db_session: SQLSession = Session()

        players = (
            db_session.query(DBPlayerName)
            .filter(DBPlayerName.league_name == league_name)
            .all()
        )

        result = [
            PlayerName(
                league_name=player.league_name,
                team_name=player.team_name,
                sports_name=player.sports_name,
                fbref_name=player.fbref_name,
                name=player.name
            ) 
            for player in players
        ]

        db_session.commit()
        db_session.close()

        return result

    def add_sports_info_to_players_stats(
            self, 
            league_name: str, 
            players_stats: PlayersLeagueStats, 
            sports_players: List[SportsPlayerDiff]
        ) -> PlayersLeagueStats:
        # get teams info
        teams_names = self.get_teams(league_name)
        teams_info = pd.DataFrame([
            {
                "team": team.fbref_name,
                "sports_team": team.sports_name,
            }
            for team in teams_names
        ])
        
        # get players info
        players_names = self.get_players(league_name)
        players_sports_2_fbref = {
            player.sports_name: player.fbref_name for player in players_names
        }
        players_info = pd.DataFrame([
            {
                "name": players_sports_2_fbref.get(player.name),
                "sports_name": player.name,
                "sports_team": player.team_name,
                "role": player.role,
                "price": player.price,
                "percent_ownership": player.percent_ownership,
                "percent_ownership_diff": player.percent_ownership_diff
            }
            for player in sports_players
        ])

        # drop sports columns
        result = deepcopy(players_stats)
        result.abs_stats.drop(
            labels=["sports_team", "sports_name", "role", "price", "percent_ownership", "percent_ownership_diff"],
            axis=1,
            inplace=True,
            errors="ignore"
        )
        result.norm_stats.drop(
            labels=["sports_team", "sports_name", "role", "price", "percent_ownership", "percent_ownership_diff"],
            axis=1,
            inplace=True,
            errors="ignore"
        )
        result.free_kicks.drop(
            labels=["sports_team", "sports_name", "role", "price", "percent_ownership", "percent_ownership_diff"],
            axis=1,
            inplace=True,
            errors="ignore"
        )

        # join teams and players info
        result.abs_stats = result.abs_stats.merge(teams_info, how="left", on="team")
        result.norm_stats = result.norm_stats.merge(teams_info, how="left", on="team")
        result.free_kicks = result.free_kicks.merge(teams_info, how="left", on="team")
        result.abs_stats = result.abs_stats.merge(players_info, how="left", on=["name", "sports_team"])
        result.norm_stats = result.norm_stats.merge(players_info, how="left", on=["name", "sports_team"])
        result.free_kicks = result.free_kicks.merge(players_info, how="left", on=["name", "sports_team"])

        return result
