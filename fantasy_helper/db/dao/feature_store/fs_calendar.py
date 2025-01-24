import os.path as path
from typing import Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession


from fantasy_helper.db.dao.table import TableDao
from fantasy_helper.db.dao.schedule import ScheduleDao
from fantasy_helper.db.dao.ml.naming import NamingDAO
from fantasy_helper.db.models.feature_store.fs_calendars import FSCalendars
from fantasy_helper.db.database import Session
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import CalendarInfo, LeagueInfo, LeagueScheduleInfo, LeagueTableInfo, SportsTourInfo


class FSCalendarsDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._schedule_dao = ScheduleDao()
        self._table_dao = TableDao()
        self._naming_dao = NamingDAO()

        self._valid_leagues = []
        for league in self._leagues:
            if league.name in self._schedule_dao.get_leagues() \
                and league.name in self._table_dao.get_leagues():
                self._valid_leagues.append(league.name)

    def _prepare_league_table(self, league_name: str) -> Dict[str, LeagueTableInfo]:
        table: List[LeagueTableInfo] = self._table_dao.get_table(league_name)

        result = {}
        for table_row in table:
            result[table_row.team_name] = table_row

        return result

    def _prepare_league_schedule(self, league_name: str) -> List[LeagueScheduleInfo]:
        schedule: List[LeagueScheduleInfo] = self._schedule_dao.get_schedule(league_name)
        
        result = []
        for schedule_row in sorted(schedule, key=lambda x: x.date):
            if schedule_row.home_goals is None and schedule_row.away_goals is None:
                result.append(schedule_row)

        return result

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
        elif val < q_2:
            return "#EBA654" # "#E57878"
        elif val > q_4:
            return "#85DE6F"
        elif val >= q_3:
            return "#EBE054" # "#85DE6F"
        else:
            return ""

    def _compute_color_for_score(
            self, 
            all_scores: Optional[np.ndarray],
            score: Optional[float],
            opponent_score: Optional[float],
    ) -> Optional[str]:
        if score is None or opponent_score is None or all_scores is None or all_scores.size == 0:
            return None

        quantile = (all_scores<score).mean()
        opponent_quantile = (all_scores<opponent_score).mean()
        diff = quantile - opponent_quantile

        if diff <= -0.5:
            return "#E06456"
        elif diff < 0.0:
            return "#EBA654" # "#E57878"
        elif diff < 0.5:
            return "#EBE054" # "#85DE6F"
        else:
            return "#85DE6F"

    def _compute_new_calendar(self, league_name: str, max_tour_count: int = 5) -> List[CalendarInfo]:
        prepared_schedule = self._prepare_league_schedule(league_name)
        prepared_table = self._prepare_league_table(league_name)
        result = []
        if len(prepared_schedule) == 0 or len(prepared_table) == 0:
            return result

        points_scores = np.array([self._compute_points_score(team) for team in prepared_table.values()])
        goals_scores = np.array([self._compute_goals_score(team) for team in prepared_table.values()])
        xg_scores = np.array(
            list(
                filter(
                    lambda x: x is not None, 
                    [self._compute_xg_score(team) for team in prepared_table.values()]
                )
            )
        )

        teams_names = self._naming_dao.get_teams(league_name)
        sports_team_2_table_row = {
            team.sports_name: prepared_table.get(team.fbref_name)
            for team in teams_names
        }

        for match in prepared_schedule:
            home_team_table_row = sports_team_2_table_row.get(match.home_team)
            away_team_table_row = sports_team_2_table_row.get(match.away_team)

            result.append(
                CalendarInfo(
                    league_name=match.league_name,
                    home_team=match.home_team,
                    away_team=match.away_team,
                    tour=match.gameweek,
                    home_points_color=self._compute_color_for_score(
                        points_scores,
                        self._compute_points_score(home_team_table_row),
                        self._compute_points_score(away_team_table_row), 
                    ),
                    away_points_color=self._compute_color_for_score(
                        points_scores,
                        self._compute_points_score(away_team_table_row),
                        self._compute_points_score(home_team_table_row),
                    ),
                    home_goals_color=self._compute_color_for_score(
                        goals_scores,
                        self._compute_goals_score(home_team_table_row),
                        self._compute_goals_score(away_team_table_row),
                    ),
                    away_goals_color=self._compute_color_for_score(
                        goals_scores,
                        self._compute_goals_score(away_team_table_row),
                        self._compute_goals_score(home_team_table_row),
                    ),
                    home_xg_color=self._compute_color_for_score(
                        xg_scores,
                        self._compute_xg_score(home_team_table_row),
                        self._compute_xg_score(away_team_table_row),
                    ),
                    away_xg_color=self._compute_color_for_score(
                        xg_scores,
                        self._compute_xg_score(away_team_table_row),
                        self._compute_xg_score(home_team_table_row),
                    )
                )
            )

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
                home_points_color=calendar_row.home_points_color,
                away_points_color=calendar_row.away_points_color,
                home_goals_color=calendar_row.home_goals_color,
                away_goals_color=calendar_row.away_goals_color,
                home_xg_color=calendar_row.home_xg_color,
                away_xg_color=calendar_row.away_xg_color
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
