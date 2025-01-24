from dataclasses import asdict
from datetime import datetime, timezone
from typing import List
import os.path as path

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_, func

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.schedule import Schedule
from fantasy_helper.db.models.table import Table
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo, SportsMatchInfo


utc = timezone.utc


class ScheduleDao:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
        )

    def get_leagues(self) -> List[str]:
        return [league.name for league in self._leagues]

    def get_schedule(self, league_name: str) -> List[LeagueScheduleInfo]:
        current_datetime = datetime.now()

        db_session: SQLSession = Session()

        all_league_schedules = (
            db_session.query(Schedule)
            .filter(and_(
                Schedule.league_name == league_name,
                Schedule.date >= current_datetime.date()
            ))
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

        latest_schedule_rows = db_session.query(grouped_by_games).filter(
            grouped_by_games.c.row_number == 1
        ).all() # .distinct()

        db_session.commit()
        db_session.close()

        result = [
            LeagueScheduleInfo(
                league_name=schedule_row.league_name,
                home_team=schedule_row.home_team,
                away_team=schedule_row.away_team,
                gameweek=schedule_row.gameweek,
                date=schedule_row.date,
                home_goals=schedule_row.home_goals,
                away_goals=schedule_row.away_goals,
            ) 
            for schedule_row in latest_schedule_rows
        ]
        return result

    def update_schedules_all_leagues(self) -> None:
        for league_name in self._sports_parser.get_leagues():
            schedule_rows: List[SportsMatchInfo] = self._sports_parser.get_next_matches(
                league_name=league_name, tour_count=5
            )

            db_session: SQLSession = Session()

            for match in schedule_rows:
                db_session.add(
                    Schedule(
                        league_name=league_name,
                        home_team=match.home_team,
                        away_team=match.away_team,
                        gameweek=match.tour_number,
                        date=match.scheduled_at_datetime.date() if match.scheduled_at_datetime else None,
                        timestamp=datetime.now().replace(tzinfo=utc)
                    )
                )

            db_session.commit()
            db_session.close()
