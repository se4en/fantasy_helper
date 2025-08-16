from dataclasses import asdict
from datetime import datetime, timezone
from typing import List, Optional
import os.path as path

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_, func
from loguru import logger

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
        self._league_2_year = {league.name: league.year for league in self._leagues}
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
        )

    def get_leagues(self) -> List[str]:
        return [league.name for league in self._leagues]

    def get_schedule(self, league_name: str, year: str = "2024") -> List[LeagueScheduleInfo]:
        current_datetime = datetime.now()

        db_session: SQLSession = Session()

        all_league_schedules = (
            db_session.query(Schedule)
            .filter(and_(
                Schedule.league_name == league_name,
                Schedule.year == year,
                Schedule.date >= current_datetime.date()
            ))
            .subquery()
        )

        latest_timestamp = db_session.query(
            func.max(all_league_schedules.c.timestamp)
        ).scalar()

        if latest_timestamp is None:
            latest_league_schedules = all_league_schedules
        else:
            latest_league_schedules = db_session.query(all_league_schedules).filter(
                func.DATE(all_league_schedules.c.timestamp) == latest_timestamp.date()
            ).subquery()

        grouped_by_games = db_session.query(
            latest_league_schedules,
            func.row_number()
            .over(
                order_by=(latest_league_schedules.c.timestamp.desc()),
                partition_by=(
                    latest_league_schedules.c.home_team,
                    latest_league_schedules.c.away_team,
                    latest_league_schedules.c.gameweek,
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
                tour_name=schedule_row.tour_name,
                date=schedule_row.date,
                home_goals=schedule_row.home_goals,
                away_goals=schedule_row.away_goals,
            ) 
            for schedule_row in latest_schedule_rows
        ]
        return result

    def get_current_tour_number(self, league_name: str) -> Optional[int]:
        league_year = self._league_2_year.get(league_name)
        schedule = self.get_schedule(league_name, league_year)
        if not schedule:
            return None

        ordered_schedule = sorted(schedule, key=lambda x: x.date)
        min_gameweek = ordered_schedule[0].gameweek

        return min_gameweek

    def get_next_tour_number(self, league_name: str) -> Optional[int]:
        league_year = self._league_2_year.get(league_name)
        schedule = self.get_schedule(league_name, league_year)
        if not schedule:
            return None

        ordered_schedule = sorted(schedule, key=lambda x: x.date)
        min_gameweek = ordered_schedule[0].gameweek

        return min_gameweek + 1

    def get_next_matches(self, league_name: str, tour_count: int) -> List[LeagueScheduleInfo]:
        league_year = self._league_2_year.get(league_name)
        schedule = self.get_schedule(league_name, league_year)
        if not schedule:
            return []

        ordered_schedule = sorted(schedule, key=lambda x: x.date)
        min_gameweek = ordered_schedule[0].gameweek
        result = []
        for match in ordered_schedule:
            if match.gameweek >= min_gameweek and match.gameweek < min_gameweek + tour_count:
                result.append(match)

        return result

    def update_schedules_all_leagues(self) -> None:
        for league_name in self._sports_parser.get_leagues():
            self.update_schedules(league_name)

    def update_schedules(self, league_name: str) -> None:
        if league_name in self._sports_parser.get_leagues():
            logger.info(f"Start update sports schedules for {league_name}")
            league_year = self._league_2_year.get(league_name)

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
                        tour_name=match.tour_name,
                        date=match.scheduled_at_datetime.date() if match.scheduled_at_datetime else None,
                        timestamp=datetime.now().replace(tzinfo=utc),
                        year=league_year
                    )
                )

            db_session.commit()
            db_session.close()

            logger.info(f"Updated {len(schedule_rows)} sports schedule rows for {league_name}")
        else:
            logger.info(f"{league_name} not in sports parser")
