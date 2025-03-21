from datetime import datetime, timezone
from typing import List, Literal

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.feature_store.fs_coeffs import FSCoeffs
from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import CoeffTableRow, MatchInfo


utc = timezone.utc


class FSCoeffsDAO:
    def get_coeffs(
        self, league_name: str) -> List[CoeffTableRow]:
        db_session: SQLSession = Session()

        cur_tour_matches = (
            db_session.query(FSCoeffs)
            .filter(FSCoeffs.league_name == league_name)
            .all()
        )

        result = [
            CoeffTableRow(
                team_name=match.team_name,
                league_name=match.league_name,
                tour_names=match.tour_names,
                tour_numbers=match.tour_numbers,
                tour_rivals=match.tour_rivals,
                tour_match_types=match.tour_match_types,
                tour_attack_coeffs=match.tour_attack_coeffs,
                tour_deffence_coeffs=match.tour_deffence_coeffs,
                tour_attack_colors=match.tour_attack_colors,
                tour_deffence_colors=match.tour_deffence_colors
            )
            for match in cur_tour_matches
        ]

        db_session.commit()
        db_session.close()

        return result

    def _get_unique_teams(self, matches: List[MatchInfo]) -> List[str]:
        unique_teams = set(
            [match.home_team for match in matches] + [match.away_team for match in matches]
        )
        return sorted(unique_teams)
    
    def _color_coeff(
        self, val: float, th_0: float = 1.5, th_1: float = 2.0, th_2: float = 3.0
    ) -> str:
        if val is None:
            return ""
        elif val <= th_0:
            color = "#85DE6F"
        elif val <= th_1:
            color = "#EBE054"
        elif val <= th_2:
            color = "#EBA654"
        else:
            color = "#E06456"

        return color
        # return f"background-color: {color}"
    
    def _get_coeffs_rows_from_mathes(
        self, league_name: str, matches: List[MatchInfo], unique_teams: List[str]
    ) -> List[CoeffTableRow]:
        team_2_matches = dict()
        for team_name in unique_teams:
            team_2_matches[team_name] = dict()

        sorted_matches = sorted(matches, key=lambda x: x.start_datetime)

        # split matches into tours
        all_tours_names = []
        for match in sorted_matches:
            if match.tour_name is not None:
                cur_tour_name = match.tour_name
                if cur_tour_name in team_2_matches[match.home_team] or \
                    cur_tour_name in team_2_matches[match.away_team]:
                    cur_tour_name += " доп"
            elif match.tour_number is not None:
                cur_tour_name = str(match.tour_number) + " тур"
                if cur_tour_name in team_2_matches[match.home_team] or \
                    cur_tour_name in team_2_matches[match.away_team]:
                    cur_tour_name += " доп"
            else:
                cur_tour_name = "текущий тур"
                if cur_tour_name in team_2_matches[match.home_team] or \
                    cur_tour_name in team_2_matches[match.away_team]:
                    cur_tour_name = "следующий тур"
                if cur_tour_name in team_2_matches[match.home_team] or \
                    cur_tour_name in team_2_matches[match.away_team]:
                    cur_tour_name = "следующий тур доп"

            team_2_matches[match.home_team][cur_tour_name] = match
            team_2_matches[match.away_team][cur_tour_name] = match

            if cur_tour_name not in all_tours_names:
                all_tours_names.append(cur_tour_name)

        result = []
        for team_name, team_matches in team_2_matches.items():
            tour_names = []
            tour_numbers = []
            tour_rivals = []
            tour_match_types = []
            tour_attack_coeffs = []
            tour_deffence_coeffs = []
            tour_attack_colors = []
            tour_deffence_colors = []

            for tour_name, tour_match in team_matches.items():
                if team_name == tour_match.home_team:
                    match_type = "[д]"
                    attack_coeff = tour_match.total_1_over_1_5
                    defence_coeff = tour_match.total_2_under_0_5
                else:
                    match_type = "[г]"
                    attack_coeff = tour_match.total_2_over_1_5
                    defence_coeff = tour_match.total_1_under_0_5

                tour_names.append(tour_name)
                tour_numbers.append(tour_match.tour_number)
                tour_rivals.append(tour_match.away_team)
                tour_match_types.append(match_type)
                tour_attack_coeffs.append(attack_coeff)
                tour_deffence_coeffs.append(defence_coeff)
                tour_attack_colors.append(self._color_coeff(attack_coeff))
                tour_deffence_colors.append(self._color_coeff(defence_coeff))

            result.append(
                CoeffTableRow(
                    team_name=team_name,
                    league_name=league_name,
                    tour_names=tour_names,
                    tour_numbers=tour_numbers,
                    tour_rivals=tour_rivals,
                    tour_match_types=tour_match_types,
                    tour_attack_coeffs=tour_attack_coeffs,
                    tour_deffence_coeffs=tour_deffence_coeffs,
                    tour_attack_colors=tour_attack_colors,
                    tour_deffence_colors=tour_deffence_colors,
                )
            )

        return result

    def _get_coeffs_rows(
        self, league_name: str, matches: List[MatchInfo]
    ) -> List[CoeffTableRow]:
        unique_teams_names = self._get_unique_teams(matches)
        coeff_rows = self._get_coeffs_rows_from_mathes(
            league_name,
            matches, 
            unique_teams_names
        )
        return coeff_rows

    def update_coeffs(
        self, league_name: str, matches: List[MatchInfo]
    ) -> None:
        db_session: SQLSession = Session()

        # remove all previous matches
        db_session.query(FSCoeffs).filter(
            FSCoeffs.league_name == league_name
        ).delete()

        coeffs_rows = self._get_coeffs_rows(league_name, matches)

        # add new matches
        for coeff_row in coeffs_rows:
            db_session.add(
                FSCoeffs(
                    **coeff_row.__dict__,
                    timestamp=datetime.now().replace(tzinfo=utc),
                )
            )

        db_session.commit()
        db_session.close()
