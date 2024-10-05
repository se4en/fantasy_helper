from dataclasses import asdict
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import func

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.table import Table
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueTableInfo


utc = timezone.utc


class TableDao:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._fbref_parser = FbrefParser(leagues=self._leagues)

    def get_table(self, league_name: str) -> List[LeagueTableInfo]:
        db_session: SQLSession = Session()

        all_league_tables_rows = (
            db_session.query(Table)
            .filter(Table.league_name == league_name)
            .subquery()
        )

        grouped_by_games = db_session.query(
            all_league_tables_rows,
            func.row_number()
            .over(
                order_by=(all_league_tables_rows.c.timestamp.desc()),
                partition_by=(all_league_tables_rows.c.team_name),
            )
            .label("row_number"),
        ).subquery()

        latest_table_rows: List[Table] = db_session.query(grouped_by_games).filter(
            grouped_by_games.c.row_number == 1
        ).distinct().all()

        db_session.commit()
        db_session.close()

        result = [
            LeagueTableInfo(
                team_name=table_row.team_name,
                league_name=table_row.league_name,
                rank=table_row.rank,
                wins=table_row.wins,
                draws=table_row.draws,
                losses=table_row.losses,
                points=table_row.points,
                goals_for=table_row.goals_for,
                goals_against=table_row.goals_against,
                xg_for=table_row.xg_for,
                xg_against=table_row.xg_against,
            ) 
            for table_row in latest_table_rows
        ]
        return result

    def update_tables_all_leagues(self) -> None:
        for league_name in self._fbref_parser.get_all_leagues():
            table_rows: List[LeagueTableInfo] = self._fbref_parser.get_league_table(
                league_name
            )
            db_session: SQLSession = Session()

            for table_row in table_rows:
                db_session.add(
                    Table(
                        **asdict(table_row), timestamp=datetime.now().replace(tzinfo=utc)
                    )
                )

            db_session.commit()
            db_session.close()
