from dataclasses import asdict
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import func

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.schedule import Schedule
from fantasy_helper.db.models.table import Table
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo


utc = timezone.utc


class ScheduleDao:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._fbref_parser = FbrefParser(leagues=self._leagues)

    def get_schedule(self, league_name: str) -> List[LeagueScheduleInfo]:
        db_session: SQLSession = Session()

        all_league_schedules = (
            db_session.query(Schedule)
            .filter(Schedule.league_name == league_name)
            .subquery()
        )

        grouped_by_games = db_session.query(
            all_league_schedules,
            func.row_number()
            .over(
                order_by=(all_league_schedules.c.timestamp.desc()),
                partition_by=(
                    all_league_schedules.c.home_team,
                    all_league_schedules.c.away_team,
                    all_league_schedules.c.gameweek,
                ),
            )
            .label("row_number"),
        ).subquery()

        latest_schedule_rows: List[Table] = db_session.query(grouped_by_games).filter(
            grouped_by_games.c.row_number == 1
        ).distinct().order_by(grouped_by_games.c.date.asc()).all()

        db_session.commit()
        db_session.close()

        result = [
            LeagueScheduleInfo(
                league_name=table_row.league_name,
                home_team=table_row.home_team,
                away_team=table_row.away_team,
                gameweek=table_row.gameweek,
                date=table_row.date,
                home_goals=table_row.home_goals,
                away_goals=table_row.away_goals,
            ) 
            for table_row in latest_schedule_rows
        ]
        return result

    def update_schedules_all_leagues(self) -> None:
        for league_name in self._fbref_parser.get_all_leagues():
            table_rows: List[LeagueScheduleInfo] = self._fbref_parser.get_league_schedule(
                league_name
            )
            db_session: SQLSession = Session()

            for table_row in table_rows:
                db_session.add(
                    Schedule(
                        **asdict(table_row), timestamp=datetime.now().replace(tzinfo=utc)
                    )
                )

            db_session.commit()
            db_session.close()
