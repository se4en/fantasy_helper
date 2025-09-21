from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict
from typing import List
from datetime import datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession
import pandas as pd
from loguru import logger

from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo, MatchInfo, PlayerName, PlayerStatsInfo, SportsMatchInfo, SportsPlayerDiff, TeamName, PlayersLeagueStats
from fantasy_helper.db.database import Session
from fantasy_helper.db.models.ml.player_name import PlayerName as DBPlayerName
from fantasy_helper.db.models.ml.team_name import TeamName as DBTeamName
from fantasy_helper.ml.naming.name_matcher import NameMatcher


utc = timezone.utc


class NamingDAO:
    def __init__(self, logger = None):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._league_2_year = {league.name: league.year for league in self._leagues}
        self._name_matcher = NameMatcher()

    def update_league_naming(self, league_name: str) -> None:
        logger.info(f"Updating naming for league {league_name}")
        year = self._league_2_year.get(league_name, "2024")
        teams_names = self._get_teams_names(league_name, year)
        logger.info(f"Found {len(teams_names)} teams names for league {league_name}")

        # update teams names
        teams_names_to_add, teams_names_to_delete = self._name_matcher.match_teams(
            league_name=league_name, 
            teams_names=teams_names
        )
        logger.info(f"Adding {len(teams_names_to_add)}, deleting {len(teams_names_to_delete)} teams names for league {league_name}")
        self._delete_teams_names(teams_names_to_delete)
        self._add_teams_names(teams_names_to_add)

        # update players names
        new_teams_names = self._get_teams_names(league_name)
        for team_name in new_teams_names:
            players_names = self._get_players_names(league_name, team_name.name)
            logger.info(f"Found {len(players_names)} players names for team {team_name.name} in {league_name}")
            players_names_to_add, players_names_to_delete = self._name_matcher.match_players(
                league_name=league_name, 
                team_name=team_name,
                players_names=players_names
            )
            logger.info(f"Adding {len(players_names_to_add)}, deleting {len(players_names_to_delete)} players names for team {team_name.name} in {league_name}")
            self._delete_players_names(players_names_to_delete)
            self._add_players_names(players_names_to_add)

    def _get_teams_names(self, league_name: str, year: str = "2024") -> List[TeamName]:
        db_session: SQLSession = Session()

        teams_names = (
            db_session.query(DBTeamName)
            .filter(and_(
                DBTeamName.league_name == league_name,
                DBTeamName.year == year
            ))
            .all()
        )

        result = [
            TeamName(
                league_name=team.league_name,
                sports_name=team.sports_name,
                fbref_name=team.fbref_name,
                xbet_name=team.xbet_name,
                betcity_name=team.betcity_name,
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
            year = self._league_2_year.get(team_name.league_name, "2024")
            db_session.add(DBTeamName(
                timestamp=datetime.now().replace(tzinfo=utc), 
                year=year,
                **asdict(team_name)
            ))

        db_session.commit()
        db_session.close()

    def _delete_teams_names(self, teams_names: List[TeamName]) -> None:
        db_session: SQLSession = Session()

        for team_name in teams_names:
            year = self._league_2_year.get(team_name.league_name, "2024")
            db_session.query(DBTeamName).filter(and_(
                DBTeamName.league_name == team_name.league_name,
                DBTeamName.name == team_name.name,
                DBTeamName.sports_name == team_name.sports_name,
                DBTeamName.fbref_name == team_name.fbref_name,
                DBTeamName.xbet_name == team_name.xbet_name,
                DBTeamName.xbet_name == team_name.betcity_name,
                DBTeamName.year == year
            )).delete()

        db_session.commit()
        db_session.close()

    def _get_players_names(self, league_name: str, team_name: str) -> List[PlayerName]:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        players_names = (
            db_session.query(DBPlayerName)
            .filter(and_(
                DBPlayerName.league_name == league_name, 
                DBPlayerName.year == year,
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
            year = self._league_2_year.get(player_name.league_name, "2024")
            db_session.add(DBPlayerName(
                timestamp=datetime.now().replace(tzinfo=utc), 
                year=year,
                **asdict(player_name)
            ))

        db_session.commit()
        db_session.close()

    def _delete_players_names(self, players_names: List[PlayerName]) -> None:
        db_session: SQLSession = Session()

        for player_name in players_names:
            year = self._league_2_year.get(player_name.league_name, "2024")
            db_session.query(DBPlayerName).filter(and_(
                DBPlayerName.league_name == player_name.league_name,
                DBPlayerName.name == player_name.name,
                DBPlayerName.team_name == player_name.team_name,
                DBPlayerName.sports_name == player_name.sports_name,
                DBPlayerName.fbref_name == player_name.fbref_name,
                DBPlayerName.year == year
            )).delete()

        db_session.commit()
        db_session.close()

    def update_naming_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_league_naming(league.name)

    def get_teams(self, league_name: str) -> List[TeamName]:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        teams = (
            db_session.query(DBTeamName)
            .filter(and_(
                DBTeamName.league_name == league_name, 
                DBTeamName.year == year
            ))
            .all()
        )

        result = [
            TeamName(
                league_name=team.league_name,
                sports_name=team.sports_name,
                fbref_name=team.fbref_name,
                xbet_name=team.xbet_name,
                betcity_name=team.betcity_name,
                name=team.name
            ) 
            for team in teams
        ]

        db_session.commit()
        db_session.close()
    
        return result

    def get_players(self, league_name: str) -> List[PlayerName]:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        players = (
            db_session.query(DBPlayerName)
            .filter(and_(
                DBPlayerName.league_name == league_name,
                DBPlayerName.year == year
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
        if "team" in result.abs_stats.columns:
            result.abs_stats = result.abs_stats.merge(teams_info, how="left", on="team")
            if "sports_team" in result.abs_stats.columns:
                result.abs_stats = result.abs_stats.merge(players_info, how="left", on=["name", "sports_team"])
        if "team" in result.norm_stats.columns:
            result.norm_stats = result.norm_stats.merge(teams_info, how="left", on="team")
            if "sports_team" in result.norm_stats.columns:
                result.norm_stats = result.norm_stats.merge(players_info, how="left", on=["name", "sports_team"])
        if "team" in result.free_kicks.columns:
            result.free_kicks = result.free_kicks.merge(teams_info, how="left", on="team")
            if "sports_team" in result.free_kicks.columns:
                result.free_kicks = result.free_kicks.merge(players_info, how="left", on=["name", "sports_team"])

        return result
    
    def add_sports_info_to_players_stats_info(
            self, 
            league_name: str, 
            players_stats_info: List[PlayerStatsInfo], 
            sports_players: List[SportsPlayerDiff]
        ) -> List[PlayerStatsInfo]:
        # get teams info
        teams_names = self.get_teams(league_name)
        teams_sports_2_fbref = {
            team.sports_name: team.fbref_name for team in teams_names
        }

        # get players info
        players_names = self.get_players(league_name)
        players_sports_2_fbref = {
            player.sports_name: player.fbref_name for player in players_names
        }

        # sports info
        fbref_2_sports_players = {}
        for player in sports_players:
            fbref_name = players_sports_2_fbref.get(player.name)
            fbref_team = teams_sports_2_fbref.get(player.team_name)
            if fbref_name and fbref_team:
                fbref_2_sports_players[(fbref_name, fbref_team)] = player

        # add sports info
        result = []
        for player_stats_info in players_stats_info:
            cur_player_stats_info = deepcopy(player_stats_info)
            sports_player = fbref_2_sports_players.get(
                (player_stats_info.name, player_stats_info.team)
            )
            if sports_player is not None:
                cur_player_stats_info.sports_name = sports_player.name
                cur_player_stats_info.sports_team = sports_player.team_name
                cur_player_stats_info.role = sports_player.role
                cur_player_stats_info.price = sports_player.price
                cur_player_stats_info.percent_ownership = sports_player.percent_ownership
                cur_player_stats_info.percent_ownership_diff = sports_player.percent_ownership_diff
            result.append(cur_player_stats_info)

        return result

    def add_sports_info_to_coeffs(
            self,
            league_name: str,
            coeffs: List[MatchInfo],
            sports_matches: List[LeagueScheduleInfo]
        ) -> List[MatchInfo]:
        teams_names = self.get_teams(league_name)
        
        betcity_team_2_sports = {
            team.betcity_name: team.sports_name
            for team in teams_names
        }

        teams_2_coeffs = {
            (
                betcity_team_2_sports.get(coeff.home_team), 
                betcity_team_2_sports.get(coeff.away_team)
            ): coeff
            for coeff in coeffs
        }

        result = []
        for match in sports_matches:
            coeff_match = teams_2_coeffs.get((match.home_team, match.away_team))
            if coeff_match is not None:
                coeff_match.home_team = match.home_team
                coeff_match.away_team = match.away_team
                coeff_match.tour_number = match.gameweek
                coeff_match.tour_name = match.tour_name
                result.append(coeff_match)
            else:  # add match with None coeffs
                result.append(MatchInfo(
                    league_name=league_name,
                    home_team=match.home_team,
                    away_team=match.away_team,
                    tour_number=match.gameweek,
                    tour_name=match.tour_name
                ))

        return result
