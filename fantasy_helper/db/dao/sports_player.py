from typing import List
from datetime import datetime, timezone
import os.path as path

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.dao.feature_store.fs_sports_players import FSSportsPlayersDAO
from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, SportsPlayerDiff
from fantasy_helper.utils.common import instantiate_leagues, load_config


utc = timezone.utc


class SportsPlayerDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../parsers/queries")
        )

    @staticmethod
    def _compute_popularity_diff(group: pd.DataFrame) -> pd.DataFrame:
        group = group[~group["percent_ownership"].isna()]
        if len(group) == 0:
            return pd.DataFrame()
        sorted_df = group.sort_values("timestamp", ascending=True)

        min_row = sorted_df.iloc[0].to_dict()
        max_row = sorted_df.iloc[-1].to_dict()

        result = [SportsPlayerDiff(
            name=min_row["name"],
            league_name=min_row["league_name"],
            team_name=min_row["team_name"] or max_row["team_name"],
            role=min_row["role"] or max_row["role"],
            price=min_row["price"] or max_row["price"],
            percent_ownership=max_row["percent_ownership"],
            percent_ownership_diff=max_row["percent_ownership"] - min_row["percent_ownership"],
        )]

        return pd.DataFrame(result)

    def get_players(self, league_name) -> List[SportsPlayerDiff]:
        tour_info = self._sports_parser.get_cur_tour_info(league_name)
        if tour_info is None or tour_info.get("number") is None:
            return None
        tour_number = tour_info["number"]
        db_session: SQLSession = Session()
        
        cur_tour_rows = db_session.query(SportsPlayer).filter(
            and_(SportsPlayer.league_name == league_name, SportsPlayer.tour == tour_number)
        )

        df = pd.read_sql(cur_tour_rows.statement, cur_tour_rows.session.bind)

        db_session.commit()
        db_session.close()

        result = df.groupby(by=["sports_id"]) \
            .apply(SportsPlayerDAO._compute_popularity_diff) \
            .reset_index(drop=True, inplace=False)

        return [SportsPlayerDiff(**row[1]) for row in result.iterrows()]

    def update_players(self, league_name) -> None:
        players_stats = self._sports_parser.get_players_stats_info(league_name)
        db_session: SQLSession = Session()
        
        for player_stats in players_stats:
            db_session.add(
                SportsPlayer(
                    **player_stats.__dict__,
                    timestamp=datetime.now().replace(tzinfo=utc),
                )
            )

        db_session.commit()
        db_session.close()

    def update_players_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_players(league.name)

    def update_feature_store(self) -> None:
        feature_store = FSSportsPlayersDAO()

        for league in self._leagues:
            players = self.get_players(league.name)
            feature_store.update_sports_players(league.name, players)
