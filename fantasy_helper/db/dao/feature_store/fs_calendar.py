import os.path as path
<<<<<<< HEAD
from typing import Dict, List, Literal, Optional

import numpy as np
=======
from typing import Dict, List, Optional

>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
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


<<<<<<< HEAD
class FSCalendarsDAO:
=======
class FSCalendarDAO:
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
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

<<<<<<< HEAD
    def _compute_points_score(self, team: LeagueTableInfo) -> float:
        return team.points

    def _compute_goals_score(self, team: LeagueTableInfo) -> float:
        return team.goals_for - team.goals_against

    def _compute_xg_score(self, team: LeagueTableInfo) -> Optional[float]:
        if team.xg_for is None or team.xg_against is None:
            return None
        else:
            return team.xg_for - team.xg_against

    @staticmethod
    def _get_value_color(
        val: Optional[float], q_1: float, q_2: float, q_3: float, q_4: float
    ) -> str:
        if val is None or pd.isna(val):
            return ""
        elif val <= q_1:
            return "#E06456"
        elif val <= q_2:
            return "#EBA654" # "#E57878"
        elif val > q_4:
            return "#85DE6F"
        elif val > q_3:
            return "#EBE054" # "#85DE6F"
        else:
            return ""

    def _compute_colors_for_table(
            self, 
            table: Dict[str, LeagueTableInfo], 
            type: Literal["points", "goals", "xg"]
    ) -> Dict[str, str]:
        if type == "points":
            score_func = self._compute_points_score
        elif type == "goals":
            score_func = self._compute_goals_score
        else:
            score_func = self._compute_xg_score

        teams_scores = {
            team_name: score_func(team)
            for team_name, team in table.items()
        }
        teams_scores_values = list(filter(lambda x: x is not None, teams_scores.values()))
        if len(teams_scores_values) == 0:
            return {}

        q1 = np.percentile(teams_scores_values, q=25)
        q2 = np.percentile(teams_scores_values, q=50)
        q3 = np.percentile(teams_scores_values, q=75)

        result = {}
        for team_name, team_score in teams_scores.items():
            result[team_name] = self._get_value_color(team_score, q1, q2, q2, q3)

        return result

=======
    def _compute_points_score(self, team_1: LeagueTableInfo, team_2: LeagueTableInfo) -> Optional[float]:
        return team_1.points - team_2.points

    def _compute_xg_score(self, team_1: LeagueTableInfo, team_2: LeagueTableInfo) -> Optional[float]:
        if team_1.xg_for is None or team_1.xg_against is None or team_2.xg_for is None or team_2.xg_against is None:
            return None
        else:
            return team_1.xg_for - team_1.xg_against - team_2.xg_for + team_2.xg_against
    
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
    def _compute_new_calendar(self, league_name: str, max_tour_count: int = 5) -> List[CalendarInfo]:
        prepared_schedule = self._prepare_league_schedule(league_name)
        prepared_table = self._prepare_league_table(league_name)
        sports_tours = self._get_sports_tours(league_name, max_tour_count)
        result = []
        if len(prepared_schedule) == 0 or len(prepared_table) == 0 or len(sports_tours) == 0:
            return result

<<<<<<< HEAD
        points_colors_table = self._compute_colors_for_table(prepared_table, type="points")
        goals_colors_table = self._compute_colors_for_table(prepared_table, type="goals")
        xg_colors_table = self._compute_colors_for_table(prepared_table, type="xg")

=======
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
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
<<<<<<< HEAD
=======
                    home_team_table = prepared_table[home_team]
                    away_team_table = prepared_table[away_team]
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce

                    result.append(
                        CalendarInfo(
                            league_name=league_name,
                            home_team=home_team,
                            away_team=away_team,
                            tour=cur_sports_tour.number,
<<<<<<< HEAD
                            home_points_color=points_colors_table.get(home_team),
                            away_points_color=points_colors_table.get(away_team),
                            home_goals_color=goals_colors_table.get(home_team),
                            away_goals_color=goals_colors_table.get(away_team),
                            home_xg_color=xg_colors_table.get(home_team),
                            away_xg_color=xg_colors_table.get(away_team)
=======
                            home_points_score=self._compute_points_score(home_team_table, away_team_table),
                            away_points_score=self._compute_points_score(away_team_table, home_team_table),
                            home_xg_score=self._compute_xg_score(home_team_table, away_team_table),
                            away_xg_score=self._compute_xg_score(away_team_table, home_team_table)
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
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
<<<<<<< HEAD
                home_points_color=calendar_row.home_points_color,
                away_points_color=calendar_row.away_points_color,
                home_goals_color=calendar_row.home_goals_color,
                away_goals_color=calendar_row.away_goals_color,
                home_xg_color=calendar_row.home_xg_color,
                away_xg_color=calendar_row.away_xg_color
=======
                home_points_score=calendar_row.home_points_score,
                away_points_score=calendar_row.away_points_score,
                home_xg_score=calendar_row.home_xg_score,
                away_xg_score=calendar_row.away_xg_score
>>>>>>> 4fb80a2c42f3c964d9b4229e27cc1143e9f109ce
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
