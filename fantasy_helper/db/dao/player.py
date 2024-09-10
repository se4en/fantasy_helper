from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import asdict

import pandas as pd
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.player import Player
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import (
    LeagueInfo,
    PlayerStats,
    PlayerStatsInfo,
    FreeKicksInfo,
    PlayersLeagueStats,
)
from fantasy_helper.db.dao.feature_store.fs_players_stats import FSPlayersStatsDAO


utc = timezone.utc


class PlayerDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self.__leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self.__fbref_parser = FbrefParser(leagues=self.__leagues)

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

    def _add_shooting_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.goals = self._compute_diff_value(
            max_stats["goals"], min_stats.get("goals", 0)
        )
        stats_info.shots = self._compute_diff_value(
            max_stats["shots"], min_stats.get("shots", 0)
        )
        stats_info.shots_on_target = self._compute_diff_value(
            max_stats["shots_on_target"], min_stats.get("shots_on_target", 0)
        )
        stats_info.xg = self._compute_diff_value(max_stats["xg"], min_stats.get("xg", 0))
        stats_info.xg_np = self._compute_diff_value(
            max_stats["npxg"], min_stats.get("npxg", 0)
        )
        return stats_info

    def _add_shooting_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats.get("minutes", 0)
        stats_info.goals = self._compute_diff_value(
            max_stats["goals"], min_stats.get("goals", 0), minutes
        )
        stats_info.shots = self._compute_diff_value(
            max_stats["shots"], min_stats.get("shots", 0), minutes
        )
        stats_info.shots_on_target = self._compute_diff_value(
            max_stats["shots_on_target"], min_stats.get("shots_on_target", 0), minutes
        )
        stats_info.xg = self._compute_diff_value(
            max_stats["xg"], min_stats.get("xg", 0), minutes
        )
        stats_info.xg_np = self._compute_diff_value(
            max_stats["npxg"], min_stats.get("npxg", 0), minutes
        )
        return stats_info

    def _add_passing_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.xa = self._compute_diff_value(
            max_stats["pass_xa"], min_stats.get("pass_xa", 0)
        )
        stats_info.key_passes = self._compute_diff_value(
            max_stats["assisted_shots"], min_stats.get("assisted_shots", 0)
        )
        stats_info.passes_into_penalty_area = self._compute_diff_value(
            max_stats["passes_into_penalty_area"], min_stats.get("passes_into_penalty_area", 0)
        )
        stats_info.crosses_into_penalty_area = self._compute_diff_value(
            max_stats["crosses_into_penalty_area"],
            min_stats.get("crosses_into_penalty_area", 0),
        )
        return stats_info

    def _add_passing_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats.get("minutes", 0)
        stats_info.xa = self._compute_diff_value(
            max_stats["pass_xa"], min_stats.get("pass_xa", 0), minutes
        )
        stats_info.key_passes = self._compute_diff_value(
            max_stats["assisted_shots"], min_stats.get("assisted_shots", 0), minutes
        )
        stats_info.passes_into_penalty_area = self._compute_diff_value(
            max_stats["passes_into_penalty_area"],
            min_stats.get("passes_into_penalty_area", 0),
            minutes,
        )
        stats_info.crosses_into_penalty_area = self._compute_diff_value(
            max_stats["crosses_into_penalty_area"],
            min_stats.get("crosses_into_penalty_area", 0),
            minutes,
        )
        return stats_info

    def _add_possesion_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.touches_in_attacking_third = self._compute_diff_value(
            max_stats["touches_att_3rd"], min_stats.get("touches_att_3rd", 0)
        )
        stats_info.touches_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["touches_att_pen_area"],
            min_stats.get("touches_att_pen_area", 0),
        )
        stats_info.carries_in_attacking_third = self._compute_diff_value(
            max_stats["carries_into_final_third"],
            min_stats.get("carries_into_final_third", 0),
        )
        stats_info.carries_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["carries_into_penalty_area"],
            min_stats.get("carries_into_penalty_area", 0),
        )
        return stats_info

    def _add_possesion_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats.get("minutes", 0)
        stats_info.touches_in_attacking_third = self._compute_diff_value(
            max_stats["touches_att_3rd"],
            min_stats.get("touches_att_3rd", 0),
            minutes,
        )
        stats_info.touches_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["touches_att_pen_area"],
            min_stats.get("touches_att_pen_area", 0),
            minutes,
        )
        stats_info.carries_in_attacking_third = self._compute_diff_value(
            max_stats["carries_into_final_third"],
            min_stats.get("carries_into_final_third", 0),
            minutes,
        )
        stats_info.carries_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["carries_into_penalty_area"],
            min_stats.get("carries_into_penalty_area", 0),
            minutes,
        )
        return stats_info

    def _compute_stats_values(
        self, max_stats: Dict, min_stats: Dict, team_name: str, position: str
    ) -> Tuple[PlayerStatsInfo, PlayerStatsInfo]:
        abs_stats_info = PlayerStatsInfo(
            name=max_stats["name"],
            team=team_name,
            position=position,
        )
        norm_stats_info = PlayerStatsInfo(
            name=max_stats["name"],
            team=team_name,
            position=position,
        )
        league_name = max_stats["league_name"]

        if league_name in self.__fbref_parser.get_playing_time_leagues():
            games = self._compute_diff_value(max_stats["games"], min_stats.get("games", 0))
            abs_stats_info.games, norm_stats_info.games = games, games
            minutes = self._compute_diff_value(
                max_stats["minutes"], min_stats.get("minutes", 0)
            )
            abs_stats_info.minutes, norm_stats_info.minutes = minutes, minutes
        if league_name in self.__fbref_parser.get_shooting_leagues():
            abs_stats_info = self._add_shooting_stats_abs(
                abs_stats_info, max_stats, min_stats
            )
            norm_stats_info = self._add_shooting_stats_norm(
                norm_stats_info, max_stats, min_stats
            )
        if league_name in self.__fbref_parser.get_passing_leagues():
            abs_stats_info = self._add_passing_stats_abs(
                abs_stats_info, max_stats, min_stats
            )
            norm_stats_info = self._add_passing_stats_norm(
                norm_stats_info, max_stats, min_stats
            )
        if league_name in self.__fbref_parser.get_possession_leagues():
            abs_stats_info = self._add_possesion_stats_abs(
                abs_stats_info, max_stats, min_stats
            )
            norm_stats_info = self._add_possesion_stats_norm(
                norm_stats_info, max_stats, min_stats
            )

        return abs_stats_info, norm_stats_info

    def _compute_player_stats(
        self, group: pd.DataFrame, is_abs_stats: bool = True
    ) -> pd.DataFrame:
        group = group[~group["games"].isna()]
        sorted_df = group.sort_values("games", ascending=True)
        if len(sorted_df) == 0:
            return pd.DataFrame()
        
        abs_stats_infos, norm_stats_infos = [], []
        team_name = group["team_name"].mode().iloc[0]
        position = group["position"].mode().iloc[0]
        max_games_row = sorted_df.iloc[-1].to_dict()
        
        abs_stats_info, norm_stats_info = self._compute_stats_values(
            max_games_row, {}, team_name, position
        )
        abs_stats_infos.append(asdict(abs_stats_info))
        norm_stats_infos.append(asdict(norm_stats_info))

        for _, row in sorted_df.iloc[:-1].iterrows():
            abs_stats_info, norm_stats_info = self._compute_stats_values(
                max_games_row, row.to_dict(), team_name, position
            )
            abs_stats_infos.append(asdict(abs_stats_info))
            norm_stats_infos.append(asdict(norm_stats_info))

        if is_abs_stats and abs_stats_infos:
            return pd.DataFrame(abs_stats_infos)
        elif (not is_abs_stats) and norm_stats_infos:
            return pd.DataFrame(norm_stats_infos)
        else:
            return pd.DataFrame()

    def _compute_free_kicks_stats_values(self, stats: Dict) -> FreeKicksInfo:
        return FreeKicksInfo(
            name=stats["name"],
            games=stats["games"],
            corner_kicks=stats["corner_kicks"],
            penalty_goals=stats["pens_made"],
            penalty_shots=stats["pens_att"],
            free_kicks_shots=stats["shots_free_kicks"],
        )

    def _compute_free_kicks_stats(self, group: pd.DataFrame) -> pd.DataFrame:
        max_games = group["games"].max()
        if max_games is None or pd.isna(max_games):
            return pd.DataFrame()
        team_name = group["team_name"].mode()
        position = group["position"].mode()
        max_games_row = group[group["games"] == max_games].iloc[0].to_dict()

        free_kikcs_info = self._compute_free_kicks_stats_values(max_games_row)
        free_kikcs_info.team = team_name
        free_kikcs_info.position = position
        return pd.DataFrame(asdict(free_kikcs_info), index=[0])

    def get_teams_names(self, league_name: str) -> List[str]:
        db_session: SQLSession = Session()

        team_names = (
            db_session.query(Player.team_name)
            .filter(Player.league_name == league_name)
            .distinct()
            .all()
        )

        db_session.commit()
        db_session.close()

        return sorted([team_name[0] for team_name in team_names])

    def get_players_stats(self, league_name: str) -> PlayersLeagueStats:
        db_session: SQLSession = Session()

        cur_league_players = (
            db_session.query(Player)
            .filter(Player.league_name == league_name)
            .subquery()
        )

        grouped_by_games = db_session.query(
            cur_league_players,
            func.row_number()
            .over(
                order_by=(cur_league_players.c.timestamp.desc()),
                partition_by=(
                    cur_league_players.c.name,
                    cur_league_players.c.team_name,
                    cur_league_players.c.position,
                    cur_league_players.c.games,
                ),
            )
            .label("row_number"),
        ).subquery()

        games_stat = db_session.query(grouped_by_games).filter(
            grouped_by_games.c.row_number == 1
        )

        df = pd.read_sql(games_stat.statement, games_stat.session.bind)

        db_session.commit()
        db_session.close()

        result = PlayersLeagueStats(
            abs_stats=df.groupby(by=["name"])
            .apply(lambda x: self._compute_player_stats(x, is_abs_stats=True))
            .drop_duplicates(subset=["name", "team", "games"], ignore_index=True)
            .reset_index(drop=True, inplace=False),
            norm_stats=df.groupby(by=["name"])
            .apply(lambda x: self._compute_player_stats(x, is_abs_stats=False))
            .drop_duplicates(subset=["name", "team", "games"], ignore_index=True)
            .reset_index(drop=True, inplace=False),
            free_kicks=df.groupby(by=["name"])
            .apply(self._compute_free_kicks_stats)
            .drop_duplicates(subset=["name", "team"], ignore_index=True)
            .reset_index(drop=True, inplace=False),
        )
        return result

    def update_players_stats_all_leagues(self) -> None:
        for league_name in self.__fbref_parser.get_all_leagues():
            players_stats: List[PlayerStats] = self.__fbref_parser.get_stats_league(
                league_name
            )
            db_session: SQLSession = Session()

            for player in players_stats:
                db_session.add(
                    Player(
                        **asdict(player), timestamp=datetime.now().replace(tzinfo=utc)
                    )
                )

            db_session.commit()
            db_session.close()

    def update_feature_store(self) -> None:
        feature_store = FSPlayersStatsDAO()

        for league in self.__leagues:
            players_stats = self.get_players_stats(league.name)
            feature_store.update_players_stats(league.name, players_stats)
