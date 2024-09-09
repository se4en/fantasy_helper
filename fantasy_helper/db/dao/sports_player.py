from typing import List
from datetime import datetime, timezone
from dataclasses import asdict

import pandas as pd
from sqlalchemy import and_, func
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.utils import instantiate
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, SportsPlayerDiff

from fantasy_helper.utils.common import load_config


utc = timezone.utc


class SportsPlayerDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf")

        self._leagues: List[LeagueInfo] = instantiate(cfg.leagues)
        self._sports_parser = SportsParser(leagues=self._leagues)

    @staticmethod
    def _compute_popularity_diff(group: pd.DataFrame) -> pd.DataFrame:
        group = group[~group["percent_ownership"].isna()]
        if len(group) == 0:
            return pd.DataFrame()
        sorted_df = group.sort_values("timestamp", ascending=True)

        min_row = sorted_df.iloc[0].to_dict()
        max_row = sorted_df.iloc[-1].to_dict()

        result = [SportsPlayerDiff(
            name=min_row["name"] or max_row["name"],
            team_name=min_row["team_name"] or max_row["team_name"],
            role=min_row["role"] or max_row["role"],
            price=min_row["price"] or max_row["price"],
            percent_ownership=max_row["percent_ownership"],
            percent_ownership_diff=max_row["percent_ownership"] - min_row["percent_ownership"],
        )]

        return pd.DataFrame(result)

    def get_players(self, league_name) -> pd.DataFrame:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        if tour_info is None or tour_info.get("number") is None:
            return None
        tour_number = tour_info["number"]
        db_session: SQLSession = Session()
        
        cur_tour_rows = (
            db_session.query(SportsPlayer)
            .filter(and_(SportsPlayer.league_name == league_name, SportsPlayer.tour == tour_number))
            .subquery()
        )

        # grouped_rows = db_session.query(
        #     cur_tour_rows,
        #     func.row_number()
        #     .over(
        #         order_by=cur_tour_rows.c.timestamp.desc(),
        #         partition_by=cur_tour_rows.c.sports_id,
        #     )
        #     .label("row_number"),
        # ).subquery()

        df = pd.read_sql(cur_tour_rows.statement, cur_tour_rows.session.bind)

        db_session.commit()
        db_session.close()

        result = df.groupby(by=["sports_id"]) \
            .apply(SportsPlayerDAO._compute_popularity_diff) \
            .reset_index(drop=True, inplace=False)

        return result

    def update_players(self, league_name) -> None:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        
        players_stats = self._sports_parser.get_players_stats_info(league_name)
        db_session: SQLSession = Session()
        
        for player_stats in players_stats:
            db_session.add(
                SportsPlayer(
                    **player_stats.__dict__,
                    tour=tour_info.get("number") if tour_info is not None else None,
                    timestamp=datetime.now().replace(tzinfo=utc),
                )
            )

        db_session.commit()
        db_session.close()

    def update_players_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_players(league.name)
