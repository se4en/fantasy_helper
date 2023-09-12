from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import asdict

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.player import Player
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerStats, PlayerStatsInfo


utc = timezone.utc


class PlayerDAO:
    def __init__(self):
        if not GlobalHydra().is_initialized():
            initialize(config_path="../../conf", version_base=None)
        cfg = compose(config_name="config")

        self.__leagues: List[LeagueInfo] = instantiate(cfg.leagues)
        self.__fbref_parser = FbrefParser(leagues=self.__leagues)

    def _compute_diff_value(
        self, max_value: Any, min_value: Any, minutes: Optional[int] = None
    ) -> Any:
        if max_value is not None and min_value is not None:
            if minutes is None:
                return max_value - min_value
            else:
                return (max_value - min_value) * 90 / minutes
        else:
            return None

    def _add_shooting_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.goals = self._compute_diff_value(
            max_stats["goals"], min_stats["goals"]
        )
        stats_info.shots = self._compute_diff_value(
            max_stats["shots"], min_stats["shots"]
        )
        stats_info.shots_on_target = self._compute_diff_value(
            max_stats["shots_on_target"], min_stats["shots_on_target"]
        )
        stats_info.xg = self._compute_diff_value(max_stats["xg"], min_stats["xg"])
        stats_info.xg_np = self._compute_diff_value(
            max_stats["npxg"], min_stats["npxg"]
        )
        return stats_info

    def _add_shooting_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats["minutes"]
        stats_info.goals = self._compute_diff_value(
            max_stats["goals"], min_stats["goals"], minutes
        )
        stats_info.shots = self._compute_diff_value(
            max_stats["shots"], min_stats["shots"], minutes
        )
        stats_info.shots_on_target = self._compute_diff_value(
            max_stats["shots_on_target"], min_stats["shots_on_target"], minutes
        )
        stats_info.xg = self._compute_diff_value(
            max_stats["xg"], min_stats["xg"], minutes
        )
        stats_info.xg_np = self._compute_diff_value(
            max_stats["npxg"], min_stats["npxg"], minutes
        )
        return stats_info

    def _add_passing_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.xa = self._compute_diff_value(
            max_stats["pass_xa"], min_stats["pass_xa"]
        )
        stats_info.key_passes = self._compute_diff_value(
            max_stats["assisted_shots"], min_stats["assisted_shots"]
        )
        stats_info.passes_into_penalty_area = self._compute_diff_value(
            max_stats["passes_into_penalty_area"], min_stats["passes_into_penalty_area"]
        )
        stats_info.crosses_into_penalty_area = self._compute_diff_value(
            max_stats["crosses_into_penalty_area"],
            min_stats["crosses_into_penalty_area"],
        )
        return stats_info

    def _add_passing_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats["minutes"]
        stats_info.xa = self._compute_diff_value(
            max_stats["pass_xa"], min_stats["pass_xa"], minutes
        )
        stats_info.key_passes = self._compute_diff_value(
            max_stats["assisted_shots"], min_stats["assisted_shots"], minutes
        )
        stats_info.passes_into_penalty_area = self._compute_diff_value(
            max_stats["passes_into_penalty_area"],
            min_stats["passes_into_penalty_area"],
            minutes,
        )
        stats_info.crosses_into_penalty_area = self._compute_diff_value(
            max_stats["crosses_into_penalty_area"],
            min_stats["crosses_into_penalty_area"],
            minutes,
        )
        return stats_info

    def _add_possesion_stats_abs(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        stats_info.touches_in_attacking_third = self._compute_diff_value(
            max_stats["touches_att_3rd"], min_stats["touches_att_3rd"]
        )
        stats_info.touches_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["touches_att_pen_area"],
            min_stats["touches_att_pen_area"],
        )
        stats_info.carries_in_attacking_third = self._compute_diff_value(
            max_stats["carries_into_final_third"],
            min_stats["carries_into_final_third"],
        )
        stats_info.carries_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["carries_into_penalty_area"],
            min_stats["carries_into_penalty_area"],
        )
        return stats_info

    def _add_possesion_stats_norm(
        self, stats_info: PlayerStatsInfo, max_stats: Dict, min_stats: Dict
    ) -> PlayerStatsInfo:
        minutes = max_stats["minutes"] - min_stats["minutes"]
        stats_info.touches_in_attacking_third = self._compute_diff_value(
            max_stats["touches_att_3rd"],
            min_stats["touches_att_3rd"],
            minutes,
        )
        stats_info.touches_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["touches_att_pen_area"],
            min_stats["touches_att_pen_area"],
            minutes,
        )
        stats_info.carries_in_attacking_third = self._compute_diff_value(
            max_stats["carries_into_final_third"],
            min_stats["carries_into_final_third"],
            minutes,
        )
        stats_info.carries_in_attacking_penalty_area = self._compute_diff_value(
            max_stats["carries_into_penalty_area"],
            min_stats["carries_into_penalty_area"],
            minutes,
        )
        return stats_info

    def _compute_stats_values(
        self, max_stats: Dict, min_stats: Dict
    ) -> Tuple[PlayerStatsInfo, PlayerStatsInfo]:
        abs_stats_info = PlayerStatsInfo(
            name=max_stats["name"],
            team=max_stats["team_name"],
            position=max_stats["position"],
        )
        norm_stats_info = PlayerStatsInfo(
            name=max_stats["name"],
            team=max_stats["team_name"],
            position=max_stats["position"],
        )
        league_name = max_stats["league_name"]

        if league_name in self.__fbref_parser.get_playing_time_leagues():
            games = self._compute_diff_value(max_stats["games"], min_stats["games"])
            abs_stats_info.games, norm_stats_info.games = games, games
            minutes = self._compute_diff_value(
                max_stats["minutes"], min_stats["minutes"]
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
        self, group: pd.DataFrame, games_count: int, is_abs_stats: bool = True
    ) -> pd.DataFrame:
        max_games = group["games"].max()
        if max_games is None:
            return pd.DataFrame()
        abs_stats_info, norm_stats_info = None, None

        max_games_row = group[group["games"] == max_games].iloc[0].to_dict()
        for i in range(max_games - games_count, max_games):
            row = group[group["games"] == i]
            if len(row) > 0:
                min_games_row = row.iloc[0].to_dict()
                abs_stats_info, norm_stats_info = self._compute_stats_values(
                    max_games_row, min_games_row
                )
                break
        if is_abs_stats and abs_stats_info is not None:
            return pd.DataFrame(asdict(abs_stats_info), index=[0])
        elif (not is_abs_stats) and norm_stats_info is not None:
            return pd.DataFrame(asdict(norm_stats_info), index=[0])
        else:
            return pd.DataFrame()

    def get_players_stats(
        self, league_name: str, games_count: int, is_abs_stats: bool = True
    ) -> pd.DataFrame:
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

        return df.groupby(by=["name", "team_name", "position"]).apply(
            lambda x: self._compute_player_stats(x, games_count, is_abs_stats)
        )

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