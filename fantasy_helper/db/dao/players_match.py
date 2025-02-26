from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, List, Literal, Optional
from copy import deepcopy
import os.path as path

import numpy as np
import pandas as pd
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo, PlayerMatchStats, PlayerStats, PlayerStatsInfo
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_, func, or_, select
from sqlalchemy.sql import alias

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.players_match import PlayersMatch
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config


utc = timezone.utc


class PlayersMatchDao:
    def __init__(self, leagues: Optional[List[LeagueInfo]] = None):
        if leagues is None:
            cfg = load_config(config_path="../../conf", config_name="config")
            self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        else:
            self._leagues = leagues
        self._fbref_parser = FbrefParser(leagues=self._leagues)

    def get_leagues(self) -> List[str]:
        return [league.name for league in self._leagues]

    def _add_match_info_to_player(
        self, players: List[PlayerMatchStats], match: LeagueScheduleInfo
    ) -> List[PlayerMatchStats]:
        result = []

        for player in players:
            new_player = deepcopy(player)
            new_player.home_team = match.home_team
            new_player.away_team = match.away_team
            new_player.gameweek = match.gameweek
            new_player.date = match.date
            new_player.match_url = match.match_url
            result.append(new_player)

        return result

    def parse_matches(
        self, league_name: str, matches: List[LeagueScheduleInfo]
    ) -> List[LeagueScheduleInfo]:
        result = []

        for match in matches:
            if match.match_url is not None:
                match_players = self._fbref_parser.parse_match_stats(match.match_url, league_name)
            else:
                match_players = None

            new_match = deepcopy(match)
            if match_players:
                new_match.match_parsed = True
                match_players = self._add_match_info_to_player(match_players, new_match)
                self.add_match_players(match_players)
            else:
                new_match.match_parsed = False

            result.append(new_match)

        return result

    def add_match_players(self, players_matches: List[PlayerMatchStats]) -> None:
        db_session: SQLSession = Session()

        for players_match in players_matches:
            db_session.add(
                PlayersMatch(
                    **asdict(players_match), timestamp=datetime.now().replace(tzinfo=utc)
                )
            )

        db_session.commit()
        db_session.close()
    
    def _compute_diff_value(
        self, max_value: Any, min_value: Any, minutes: Optional[int] = None
    ) -> Any:
        if (max_value is not None and not np.isnan(max_value)) and (
            min_value is not None and not np.isnan(min_value)
        ):
            if minutes is None or np.isnan(minutes):
                return max_value - min_value
            else:
                if minutes > 0:
                    return float(max_value - min_value) * 90.0 / minutes
                else:
                    return None
        else:
            return None

    def _compute_avg_diff_value(
        self, max_value: Any, min_value: Any, min_games: Any, max_games: Any
    ) -> Any:
        if min_games is None or pd.isna(min_games) or max_games is None \
            or pd.isna(max_games) or max_games == 0 or \
                min_value is None or pd.isna(min_value):
            return None

        value_diff = self._compute_diff_value(max_value, min_value * min_games / max_games)
        games_diff = self._compute_diff_value(max_games, min_games)

        if value_diff is None or games_diff is None or games_diff == 0:
            return None

        return value_diff * max_games / games_diff

    def _convert_db_player_match_stat(
        self, 
        player_match: PlayersMatch, 
        games: int
    ) -> PlayerStatsInfo:
        return PlayerStatsInfo(
            name=player_match.name,
            team=player_match.team_name,
            position=player_match.position,
            # playing time
            games=games,
            minutes=player_match.minutes,
            # shooting
            goals=player_match.goals,
            shots=player_match.shots,
            shots_on_target=player_match.shots_on_target,
            average_shot_distance=None,
            xg=player_match.xg,
            xg_np=player_match.xg_np,
            xg_xa=player_match.xg + player_match.xg_assist,
            xg_np_xa=player_match.xg + player_match.xg_assist,
            # passing
            assists=player_match.assists,
            xa=player_match.xg_assist,
            key_passes=None,
            passes_into_penalty_area=player_match.passes_into_penalty_area,
            crosses_into_penalty_area=player_match.crosses_into_penalty_area,
            # possesion
            touches_in_attacking_third=player_match.touches_att_3rd,
            touches_in_attacking_penalty_area=player_match.touches_att_pen_area,
            carries_in_attacking_third=player_match.carries_into_final_third,
            carries_in_attacking_penalty_area=player_match.carries_into_penalty_area,
            # shot creation
            sca=player_match.sca,
            gca=player_match.gca
        )

    def get_players_match_stats(self, league_name: str) -> List[PlayerMatchStats]:
        db_session: SQLSession = Session()

        cur_league_players = (
            db_session.query(PlayersMatch)
            .filter(and_(
                PlayersMatch.league_name == league_name,
                PlayersMatch.date != None
            ))
            .subquery()
        )

        grouped_by_id = db_session.query(
            cur_league_players,
            func.row_number()
            .over(
                order_by=(cur_league_players.c.timestamp.desc()),
                partition_by=(
                    cur_league_players.c.player_id,
                    cur_league_players.c.date
                )
            )
            .label("row_number"),
        ).subquery()

        result_db = db_session.query(grouped_by_id).filter(
            grouped_by_id.c.row_number == 1
        ).all()

        result = []
        for player in result_db:
            db_player = dict(player._mapping)
            del db_player["id"]
            del db_player["row_number"]
            del db_player["timestamp"]
            result.append(PlayerMatchStats(**db_player))

        db_session.commit()
        db_session.close()

        return result
    
    def get_players_stats_info(
        self, 
        league_name: str, 
        type: Literal["abs, norm"] = "abs"
    ) -> List[PlayerStatsInfo]:
        db_session: SQLSession = Session()

        cur_league_players = (
            db_session.query(PlayersMatch)
            .filter(and_(
                PlayersMatch.league_name == league_name,
                PlayersMatch.date != None
            ))
            .subquery()
        )

        grouped_by_id = db_session.query(
            cur_league_players,
            func.row_number()
            .over(
                order_by=(cur_league_players.c.timestamp.desc()),
                partition_by=(
                    cur_league_players.c.player_id,
                    cur_league_players.c.date
                )
            )
            .label("row_number"),
        ).subquery()

        matches_stats = db_session.query(grouped_by_id).filter(
            grouped_by_id.c.row_number == 1
        ).subquery()
        # window = Window(partition_by=matches_stats.c.player_id)

        result = []
        if type == "abs":
            cumulitive_stats = db_session.query(
                # common
                matches_stats.c.name,
                matches_stats.c.player_id,
                matches_stats.c.league_name,
                matches_stats.c.team_name,
                matches_stats.c.position,
                matches_stats.c.shirt_number,
                matches_stats.c.nationality,
                matches_stats.c.player_url,
                # playing time
                func.sum(matches_stats.c.minutes).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("games"),
                func.sum(matches_stats.c.minutes).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("minutes"),
                # shooting
                func.sum(matches_stats.c.goals).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("goals"),
                func.sum(matches_stats.c.shots).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("shots"),
                func.sum(matches_stats.c.shots_on_target).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("shots_on_target"),
                func.sum(matches_stats.c.xg).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("xg"),
                func.sum(matches_stats.c.xg_np).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("xg_np"),
                # passing
                func.sum(matches_stats.c.assists).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("assists"),
                func.sum(matches_stats.c.xg_assist).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("xg_assist"),
                func.sum(matches_stats.c.passes_into_penalty_area).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("passes_into_penalty_area"),
                func.sum(matches_stats.c.crosses_into_penalty_area).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("crosses_into_penalty_area"),
                # possesion
                func.sum(matches_stats.c.touches_att_3rd).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("touches_att_3rd"),
                func.sum(matches_stats.c.touches_att_pen_area).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("touches_att_pen_area"),
                func.sum(matches_stats.c.carries_into_final_third).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("carries_into_final_third"),
                func.sum(matches_stats.c.carries_into_penalty_area).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("carries_into_penalty_area"),
                # shot creation
                func.sum(matches_stats.c.sca).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("sca"),
                func.sum(matches_stats.c.gca).over(
                    partition_by=matches_stats.c.player_id, 
                    order_by=matches_stats.c.date
                ).label("gca")
            ).all()
            for player in cumulitive_stats:
                result.append(self._convert_db_player_match_stat(player, 1))

        # result = []
        # if type is None:
        #     result_db = db_session.query(grouped_by_id).filter(
        #         grouped_by_id.c.row_number == 1
        #     ).all()

        #     for player in result_db:
        #         result.append(self._convert_db_player_match_stat(player, 1))

        db_session.commit()
        db_session.close()

        return result
