from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict
from typing import List, Literal, Optional

import numpy as np
import pandas as pd
from sqlalchemy import and_, func, union, case
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.sql.functions import coalesce

from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import PlayerStatsInfo, PlayersLeagueStats, SportsPlayerDiff
from fantasy_helper.db.models.feature_store.fs_players_free_kicks import (
    FSPlayersFreeKicks,
)
from fantasy_helper.db.models.feature_store.fs_players_stats import FSPlayersStats
from fantasy_helper.db.models.fbref_schedule import FbrefSchedule
from fantasy_helper.db.models.players_match import PlayersMatch
from fantasy_helper.db.dao.ml.naming import NamingDAO
from fantasy_helper.db.dao.feature_store.fs_sports_players import FSSportsPlayersDAO


class FSPlayersStatsDAO:
    def __init__(self):
        self._naming_dao = NamingDAO()
        self._fs_sports_players_dao = FSSportsPlayersDAO()

    def _add_empty_matches(self, players_stats: List[PlayerStatsInfo]) -> List[PlayerStatsInfo]:
        team_to_players = defaultdict(lambda: defaultdict(dict))
        team_to_max_matches = dict()

        for player_stat in players_stats:
            team_to_players[player_stat.team][player_stat.name][player_stat.games_all] = player_stat
            team_to_max_matches[player_stat.team] = max(
                team_to_max_matches.get(player_stat.team, 0), player_stat.games_all
            )

        result = []
        for team_name, team_players_stats in team_to_players.items():
            for player_name, player_stats in team_players_stats.items():
                prev_match_stat = None
                for match_number in range(1, team_to_max_matches.get(team_name, 0) + 1):
                    if match_number in player_stats:
                        prev_match_stat = deepcopy(player_stats[match_number])
                        result.append(player_stats[match_number])
                    elif prev_match_stat is not None:
                        prev_match_stat.games_all = match_number
                        result.append(deepcopy(prev_match_stat))
                    else:
                        result.append(PlayerStatsInfo(
                            team=team_name,
                            name=player_name,
                            games=0,
                            games_all=match_number,
                            minutes=0,
                            goals=0,
                            shots=0,
                            shots_on_target=0,
                            average_shot_distance=0,
                            xg=0,
                            xg_np=0,
                            xg_xa=0,
                            xg_np_xa=0,
                            assists=0,
                            xa=0,
                            key_passes=0,
                            passes_into_penalty_area=0,
                            crosses_into_penalty_area=0,
                            touches_in_attacking_third=0,
                            touches_in_attacking_penalty_area=0,
                            carries_in_attacking_third=0,
                            carries_in_attacking_penalty_area=0,
                            sca=0,
                            gca=0
                        ))

        return result

    def compute_players_stats_info(self, league_name: str) -> List[PlayerStatsInfo]:
        db_session: SQLSession = Session()

        # get all teams matches
        home_teams_matches = (
            db_session.query(
                FbrefSchedule.home_team.label("home_team"),
                FbrefSchedule.away_team.label("away_team"),
                FbrefSchedule.gameweek.label("gameweek"),
                FbrefSchedule.date.label("date"),
                FbrefSchedule.home_goals.label("home_goals"),
                FbrefSchedule.away_goals.label("away_goals"),
                FbrefSchedule.home_xg.label("home_xg"),
                FbrefSchedule.away_xg.label("away_xg"),
                FbrefSchedule.home_team.label("team_name"),
            ).filter(and_(
                FbrefSchedule.league_name == league_name,
                FbrefSchedule.match_parsed == True
            ))
        )
        away_teams_matches = (
            db_session.query(
                FbrefSchedule.home_team.label("home_team"),
                FbrefSchedule.away_team.label("away_team"),
                FbrefSchedule.gameweek.label("gameweek"),
                FbrefSchedule.date.label("date"),
                FbrefSchedule.home_goals.label("home_goals"),
                FbrefSchedule.away_goals.label("away_goals"),
                FbrefSchedule.home_xg.label("home_xg"),
                FbrefSchedule.away_xg.label("away_xg"),
                FbrefSchedule.away_team.label("team_name"),
            ).filter(and_(
                FbrefSchedule.league_name == league_name,
                FbrefSchedule.match_parsed == True
            ))
        )
        all_teams_matches = union(home_teams_matches, away_teams_matches).alias()
        ordered_teams_matches = db_session.query(
            all_teams_matches,
            func.row_number()
            .over(
                order_by=(all_teams_matches.c.date.desc()),
                partition_by=(all_teams_matches.c.team_name)
            )
            .label("match_number"),
        ).subquery()

        # get all players matches
        cur_league_players = (
            db_session.query(PlayersMatch)
            .filter(and_(
                PlayersMatch.league_name == league_name,
                PlayersMatch.date != None
            ))
            .subquery()
        )

        # join players to matches
        matches_with_players = db_session.query(
            ordered_teams_matches, cur_league_players
        ).join(
            cur_league_players,
            and_(
                ordered_teams_matches.c.home_team == cur_league_players.c.home_team,
                ordered_teams_matches.c.away_team == cur_league_players.c.away_team,
                ordered_teams_matches.c.gameweek == cur_league_players.c.gameweek,
                ordered_teams_matches.c.date == cur_league_players.c.date,
                ordered_teams_matches.c.team_name == cur_league_players.c.team_name
            ),
            isouter=True
        ).subquery()
        clean_matches_with_players = (
            db_session.query(matches_with_players)
            .filter(and_(
                matches_with_players.c.home_team != None,
                matches_with_players.c.away_team != None,
                matches_with_players.c.gameweek != None,
                matches_with_players.c.team_name != None,
                matches_with_players.c.name != None,
                matches_with_players.c.player_id != None,
                matches_with_players.c.match_number != None
            ))
            .subquery()
        )

        cumulitive_stats = db_session.query(
            # common
            clean_matches_with_players.c.name,
            clean_matches_with_players.c.team_name.label("team"),
            clean_matches_with_players.c.position,
            # playing time
            clean_matches_with_players.c.match_number.label("games_all"),
            func.sum(case(
                [(
                    coalesce(clean_matches_with_players.c.minutes, 0) > 0, 
                    1
                )], 
                else_=0
            ))
            .over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("games"),
            func.sum(clean_matches_with_players.c.minutes).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("minutes"),
            # shooting
            func.sum(clean_matches_with_players.c.goals).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("goals"),
            func.sum(clean_matches_with_players.c.shots).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("shots"),
            func.sum(clean_matches_with_players.c.shots_on_target).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("shots_on_target"),
            func.sum(clean_matches_with_players.c.xg).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("xg"),
            func.sum(clean_matches_with_players.c.xg_np).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("xg_np"),
            # passing
            func.sum(clean_matches_with_players.c.assists).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("assists"),
            func.sum(clean_matches_with_players.c.xg_assist).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("xa"),
            func.sum(clean_matches_with_players.c.passes_into_penalty_area).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("passes_into_penalty_area"),
            func.sum(clean_matches_with_players.c.crosses_into_penalty_area).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("crosses_into_penalty_area"),
            # possesion
            func.sum(clean_matches_with_players.c.touches_att_3rd).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("touches_in_attacking_third"),
            func.sum(clean_matches_with_players.c.touches_att_pen_area).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("touches_in_attacking_penalty_area"),
            func.sum(clean_matches_with_players.c.carries_into_final_third).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("carries_in_attacking_third"),
            func.sum(clean_matches_with_players.c.carries_into_penalty_area).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("carries_in_attacking_penalty_area"),
            # shot creation
            func.sum(clean_matches_with_players.c.sca).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("sca"),
            func.sum(clean_matches_with_players.c.gca).over(
                partition_by=clean_matches_with_players.c.player_id, 
                order_by=clean_matches_with_players.c.match_number
            ).label("gca")
        )

        result = []
        for row in cumulitive_stats.all():
            player_stat = PlayerStatsInfo(**dict(row._mapping))
            if player_stat.xg is not None and player_stat.xa is not None:
                player_stat.xg_xa = player_stat.xg + player_stat.xa
            if player_stat.xg_np is not None and player_stat.xa is not None:
                player_stat.xg_np_xa = player_stat.xg_np + player_stat.xa
            result.append(player_stat)

        db_session.commit()
        db_session.close()

        result = self._add_empty_matches(result)

        return result

    def get_players_stats_info(self, league_name: str) -> List[PlayerStatsInfo]:
        db_session: SQLSession = Session()

        league_players_stats = db_session.query(FSPlayersStats).filter(
            FSPlayersStats.league_name == league_name
        ).all()

        result = []
        for player_stat in league_players_stats:
            result.append(PlayerStatsInfo(
                name=player_stat.name,
                team=player_stat.team,
                position=player_stat.position,
                # playing time
                games=player_stat.games,
                games_all=player_stat.games_all,
                minutes=player_stat.minutes,
                # shooting
                goals=player_stat.goals,
                shots=player_stat.shots,
                shots_on_target=player_stat.shots_on_target,
                average_shot_distance=player_stat.average_shot_distance,
                xg=player_stat.xg,
                xg_np=player_stat.xg_np,
                xg_xa=player_stat.xg_xa,
                xg_np_xa=player_stat.xg_np_xa,
                # passing
                assists=player_stat.assists,
                xa=player_stat.xa,
                key_passes=player_stat.key_passes,
                passes_into_penalty_area=player_stat.passes_into_penalty_area,
                crosses_into_penalty_area=player_stat.crosses_into_penalty_area,
                # pass types
                touches_in_attacking_third=player_stat.touches_in_attacking_third,
                touches_in_attacking_penalty_area=player_stat.touches_in_attacking_penalty_area,
                carries_in_attacking_third=player_stat.carries_in_attacking_third,
                carries_in_attacking_penalty_area=player_stat.carries_in_attacking_penalty_area,
                # shot creation
                sca=player_stat.sca,
                gca=player_stat.gca,
                # sports info
                sports_team=player_stat.sports_team,
                sports_name=player_stat.sports_name,
                role=player_stat.role,
                price=player_stat.price,
                percent_ownership=player_stat.percent_ownership,
                percent_ownership_diff=player_stat.percent_ownership_diff  
            ))

        db_session.close()

        return result

    def update_players_stats_info(
        self,
        league_name: str,
        players_stats_info: List[PlayerStatsInfo],
        add_sports_info: bool = True
    ) -> None:
        if add_sports_info:
            sports_players = self._fs_sports_players_dao.get_sports_players(league_name)
            players_stats_info = self._naming_dao.add_sports_info_to_players_stats_info(
                league_name, players_stats_info, sports_players
            )

        db_session: SQLSession = Session()

        # remove all previous stats
        db_session.query(FSPlayersStats).filter(
            FSPlayersStats.league_name == league_name
        ).delete()

        # add new stats
        for player_stats_info in players_stats_info:
            db_session.add(FSPlayersStats(league_name=league_name, **asdict(player_stats_info)))

        db_session.commit()
        db_session.close()

    def get_players_stats(self, league_name: str) -> PlayersLeagueStats:
        """
        Retrieves the player statistics for a given league.

        Args:
            league_name (str): The name of the league.

        Returns:
            PlayersLeagueStats: An object containing the player statistics for the league. The object has the following attributes:
                - abs_stats (pandas.DataFrame): A DataFrame containing the absolute player statistics.
                - norm_stats (pandas.DataFrame): A DataFrame containing the normalized player statistics.
                - free_kicks (pandas.DataFrame): A DataFrame containing the player free kick statistics.
        """
        db_session: SQLSession = Session()

        abs_players_stats = db_session.query(FSPlayersStats).filter(
            and_(
                FSPlayersStats.league_name == league_name,
                FSPlayersStats.type == "abs",
            )
        )

        norm_players_stats = db_session.query(FSPlayersStats).filter(
            and_(
                FSPlayersStats.league_name == league_name,
                FSPlayersStats.type == "norm",
            )
        )

        players_free_kicks = db_session.query(FSPlayersFreeKicks).filter(
            FSPlayersFreeKicks.league_name == league_name
        )

        abs_players_stats_df = pd.read_sql(
            abs_players_stats.statement, abs_players_stats.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        norm_players_stats_df = pd.read_sql(
            norm_players_stats.statement, norm_players_stats.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        players_free_kicks_df = pd.read_sql(
            players_free_kicks.statement, players_free_kicks.session.bind
        ).drop_duplicates(subset=["name", "team", "games"], ignore_index=True)

        db_session.commit()
        db_session.close()

        result = PlayersLeagueStats(
            abs_stats=abs_players_stats_df,
            norm_stats=norm_players_stats_df,
            free_kicks=players_free_kicks_df,
        )

        return result

    def update_players_stats(
        self,
        league_name: str,
        add_sports_info: bool = True
    ) -> None:
        """
        Updates the player statistics for a given league.

        Args:
            league_name (str): The name of the league.
            players_stats (PlayersLeagueStats): The player statistics to update.

        Returns:
            None: This function does not return anything.
        """
        if add_sports_info:
            sports_players = self._fs_sports_players_dao.get_sports_players(league_name)
            players_stats = self._naming_dao.add_sports_info_to_players_stats(
                league_name, players_stats, sports_players
            )

        db_session: SQLSession = Session()

        # remove all previous stats
        db_session.query(FSPlayersFreeKicks).filter(
            FSPlayersFreeKicks.league_name == league_name
        ).delete()

        for index, free_kick_stats in players_stats.free_kicks.replace(
            np.nan, None
        ).iterrows():
            db_session.add(
                FSPlayersFreeKicks(league_name=league_name, **free_kick_stats)
            )

        db_session.commit()
        db_session.close()

    def get_teams_names(self, league_name: str) -> List[str]:
        db_session: SQLSession = Session()

        team_names = (
            db_session.query(FSPlayersStats.sports_team)
            .filter(FSPlayersStats.league_name == league_name)
            .distinct()
            .all()
        )

        db_session.commit()
        db_session.close()

        return sorted([team_name[0] for team_name in team_names if team_name[0] is not None])

    def get_players_names(self, league_name: str, team_name: str) -> List[str]:
        db_session: SQLSession = Session()

        player_names = (
            db_session.query(FSPlayersStats.sports_name)
            .filter(and_(FSPlayersStats.league_name == league_name, FSPlayersStats.sports_team == team_name))
            .distinct()
            .all()
        )

        db_session.commit()
        db_session.close()

        return sorted([player_name[0] for player_name in player_names if player_name[0] is not None])
