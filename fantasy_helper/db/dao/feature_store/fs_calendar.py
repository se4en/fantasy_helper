import os.path as path
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession


from fantasy_helper.db.dao.table import TableDao
from fantasy_helper.db.dao.schedule import ScheduleDao
from fantasy_helper.db.models.feature_store.fs_calendars import FSCalendars
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import CalendarInfo, LeagueInfo, LeagueScheduleInfo, LeagueTableInfo, SportsTourInfo


class FSCalendarDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._schedule_dao = ScheduleDao()
        self._table_dao = TableDao()
        self._sports_parser = SportsParser(
            leagues=self._leagues,
            queries_path=path.join(path.dirname(__file__), "../../../parsers/queries"),
        )

        self._valid_leagues = []
        for league in self._leagues:
            if league.name in self._schedule_dao.get_leagues() \
                and league.name in self._table_dao.get_leagues() \
                and league.name in self._sports_parser.get_leagues():
                self._valid_leagues.append(league.name)

    def _prepare_league_table(self, league_name: str) -> Dict[str, LeagueTableInfo]:
        table: List[LeagueTableInfo] = self._table_dao.get_table(league_name)

        result = {}
        for table_row in table:
            result[table_row.team_name] = table_row

        return result
    
    def _get_sports_tours(self, league_name: str, max_tour_count: int) -> List[SportsTourInfo]:
        sports_schedule: List[SportsTourInfo] = self._sports_parser.get_schedule(league_name)
        
        result = []
        first_tour_info = None
        for tour in sports_schedule:
            if first_tour_info is not None:
                result.append(tour)
                if len(result) == max_tour_count + 1:
                    break
            elif tour.status == "OPENED" or tour.status == "NOT_STARTED":
                result.append(tour)
                first_tour_info = tour

        return result
    
    def _prepare_league_schedule(self, league_name: str) -> List[LeagueScheduleInfo]:
        schedule: List[LeagueScheduleInfo] = self._schedule_dao.get_schedule(league_name)
        
        result = []
        for schedule_row in sorted(schedule, key=lambda x: x.date):
            if schedule_row.home_goals is None and schedule_row.away_goals is None:
                result.append(schedule_row)

        return result

    def _compute_points_score(self, team_1: LeagueTableInfo, team_2: LeagueTableInfo) -> Optional[float]:
        return team_1.points - team_2.points

    def _compute_xg_score(self, team_1: LeagueTableInfo, team_2: LeagueTableInfo) -> Optional[float]:
        if team_1.xg_for is None or team_1.xg_against is None or team_2.xg_for is None or team_2.xg_against is None:
            return None
        else:
            return team_1.xg_for - team_1.xg_against - team_2.xg_for + team_2.xg_against
    
    def _compute_new_calendar(self, league_name: str, max_tour_count: int = 5) -> List[CalendarInfo]:
        prepared_schedule = self._prepare_league_schedule(league_name)
        prepared_table = self._prepare_league_table(league_name)
        sports_tours = self._get_sports_tours(league_name, max_tour_count)
        result = []
        if len(prepared_schedule) == 0 or len(prepared_table) == 0 or len(sports_tours) == 0:
            return result

        schedule_idx = 0
        sports_tour_idx = 0
        while sports_tour_idx < len(sports_tours) and sports_tour_idx < max_tour_count:
            cur_sports_tour = sports_tours[sports_tour_idx]
            if sports_tour_idx < len(sports_tours) - 1:
                next_sports_tour = sports_tours[sports_tour_idx + 1]
            else:
                next_sports_tour = None

            # add current tour matches
            while schedule_idx < len(prepared_schedule) and \
                  (next_sports_tour is None or \
                   prepared_schedule[schedule_idx].date < next_sports_tour.deadline.date()):
                if prepared_schedule[schedule_idx].date >= cur_sports_tour.deadline.date():
                    home_team = prepared_schedule[schedule_idx].home_team
                    away_team = prepared_schedule[schedule_idx].away_team
                    home_team_table = prepared_table[home_team]
                    away_team_table = prepared_table[away_team]

                    result.append(
                        CalendarInfo(
                            league_name=league_name,
                            home_team=home_team,
                            away_team=away_team,
                            tour=cur_sports_tour.number,
                            home_points_score=self._compute_points_score(home_team_table, away_team_table),
                            away_points_score=self._compute_points_score(away_team_table, home_team_table),
                            home_xg_score=self._compute_xg_score(home_team_table, away_team_table),
                            away_xg_score=self._compute_xg_score(away_team_table, home_team_table)
                        )
                    )

                schedule_idx += 1

            sports_tour_idx += 1

        return result

    def get_calendar(self, league_name: str) -> List[CalendarInfo]:
        db_session: SQLSession = Session()

        calendar_rows = (
            db_session.query(FSCalendars)
            .filter(and_(FSCalendars.league_name == league_name))
            .all()
        )

        result = [
            CalendarInfo(
                league_name=calendar_row.league_name,
                home_team=calendar_row.home_team,
                away_team=calendar_row.away_team,
                tour=calendar_row.tour,
                home_points_score=calendar_row.home_points_score,
                away_points_score=calendar_row.away_points_score,
                home_xg_score=calendar_row.home_xg_score,
                away_xg_score=calendar_row.away_xg_score
            )
            for calendar_row in calendar_rows
        ]

        db_session.commit()
        db_session.close()

        return result

    def update_calendar(self, league_name: str) -> None:
        if league_name not in self._valid_leagues:
            return None
        new_calendar_rows = self._compute_new_calendar(league_name)
        if len(new_calendar_rows) == 0:
            return None

        db_session: SQLSession = Session()

        db_session.query(FSCalendars).filter(
            FSCalendars.league_name == league_name
        ).delete()

        for new_calendar_row in new_calendar_rows:
            db_session.add(FSCalendars(**new_calendar_row.__dict__))

        db_session.commit()
        db_session.close()

    def update_calendar_all_leagues(self) -> None:
        for league_name in self._valid_leagues:
            self.update_calendar(league_name)
